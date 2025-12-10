/// <reference path="./.sst/platform/config.d.ts" />

/**
 * Filter-iCal SST Configuration - True Serverless Architecture
 *
 * Stack:
 * - Frontend: Vue 3 SPA on CloudFront + S3
 * - Backend: FastAPI on AWS Lambda (Python 3.11)
 * - API: API Gateway HTTP API (direct Lambda integration)
 * - Database: DynamoDB (on-demand, serverless)
 * - Scheduler: EventBridge (30-minute interval for calendar sync)
 *
 * Cost (eu-north-1):
 * - Lambda: $0/month (within free tier)
 * - DynamoDB: $0/month (on-demand, free tier)
 * - API Gateway: $0/month (within free tier)
 * - CloudFront + S3: ~$2/month
 * - Secrets: ~$1/month
 * Total: ~$3/month
 *
 * NO VPC required - Lambda can reach DynamoDB and SES directly.
 */

export default $config({
  app(input) {
    return {
      name: "filter-ical",
      removal: input.stage === "production" ? "retain" : "remove",
      home: "aws",
      providers: {
        aws: {
          region: "eu-north-1",
          profile: "filter-ical"
        }
      }
    };
  },
  async run() {
    // 1. DynamoDB Table (single-table design)
    const table = new sst.aws.Dynamo("FilterIcalTable", {
      fields: {
        PK: "string",  // Partition key: DOMAIN#key, FILTER#uuid, ADMIN#email
        SK: "string",  // Sort key: METADATA, EVENT#date#uid, etc.
        link_uuid: "string",  // For filter UUID lookups (GSI)
      },
      primaryIndex: { hashKey: "PK", rangeKey: "SK" },
      globalIndexes: {
        // GSI for looking up filters by link_uuid
        LinkUuidIndex: { hashKey: "link_uuid" },
      },
      // On-demand billing (pay per request, $0 at low volume)
      billing: "on-demand",
    });

    // 2. Backend API Lambda Function (FastAPI with Mangum)
    // NO VPC - can reach DynamoDB and SES directly via public endpoints
    const backendFunction = new sst.aws.Function("FilterIcalBackendApi", {
      handler: "backend.lambda_handler.handler",
      runtime: "python3.11",
      architecture: "x86_64",
      timeout: "30 seconds",
      memory: "512 MB",

      // Docker build for Linux-compatible binaries
      python: {
        container: true,
      },

      // Link to DynamoDB table
      link: [table],

      // Environment variables
      environment: {
        PYTHONPATH: "/var/task",

        // DynamoDB table name (SST link provides this)
        DYNAMODB_TABLE_NAME: table.name,

        // Stage
        ENVIRONMENT: $dev ? "development" : $app.stage,
        IS_LAMBDA: "true",

        // Use DynamoDB instead of SQL
        USE_DYNAMODB: "true",

        // Secrets from AWS Secrets Manager
        JWT_SECRET_KEY: new sst.Secret("JwtSecretKey").value,
        ADMIN_EMAIL: new sst.Secret("AdminEmail").value,
        ADMIN_PASSWORD: new sst.Secret("AdminPassword").value,
      },

      // Permissions: SES for emails, DynamoDB via link
      permissions: [
        {
          actions: ["ses:SendEmail", "ses:SendRawEmail"],
          resources: ["arn:aws:ses:eu-north-1:*:identity/*"]
        }
      ],
    });

    // 3. API Gateway with custom domain
    const api = new sst.aws.ApiGatewayV2("FilterIcalApi", {
      domain: $dev ? undefined : ($app.stage === "production"
        ? "api.filter-ical.de"
        : `api-${$app.stage}.filter-ical.de`),
      cors: {
        allowOrigins: $app.stage === "production"
          ? ["https://filter-ical.de", "https://www.filter-ical.de"]
          : $app.stage === "staging"
          ? ["https://staging.filter-ical.de"]
          : ["http://localhost:5173", "http://localhost:8000"],
        allowMethods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allowHeaders: ["Content-Type", "Authorization", "Accept", "Accept-Language", "X-Requested-With"],
        allowCredentials: true,
      },
    });

    // Route all requests to backend Lambda
    api.route("ANY /{proxy+}", backendFunction.arn);
    api.route("ANY /", backendFunction.arn);

    // 4. Scheduled Sync Lambda Function
    const syncFunction = new sst.aws.Function("FilterIcalSyncTask", {
      handler: "backend.lambda_sync.handler",
      runtime: "python3.11",
      architecture: "x86_64",
      timeout: "5 minutes",
      memory: "512 MB",

      python: {
        container: true,
      },

      link: [table],

      environment: {
        PYTHONPATH: "/var/task",
        DYNAMODB_TABLE_NAME: table.name,
        ENVIRONMENT: $dev ? "development" : $app.stage,
        IS_LAMBDA: "true",
        USE_DYNAMODB: "true",
        JWT_SECRET_KEY: new sst.Secret("JwtSecretKey").value,
        ADMIN_EMAIL: new sst.Secret("AdminEmail").value,
        ADMIN_PASSWORD: new sst.Secret("AdminPassword").value,
      },

      permissions: [
        {
          actions: ["ses:SendEmail", "ses:SendRawEmail"],
          resources: ["arn:aws:ses:eu-north-1:*:identity/*"]
        }
      ],
    });

    // 5. EventBridge Scheduler (runs every 30 minutes)
    // Disabled for now - uncomment when ready
    // const syncScheduler = !$dev && new sst.aws.Cron("FilterIcalSyncScheduler", {
    //   schedule: "rate(30 minutes)",
    //   job: syncFunction,
    // });

    // 6. Frontend (Vue 3 SPA on CloudFront + S3)
    const frontend = new sst.aws.StaticSite("FilterIcalFrontend", {
      path: ".",
      build: {
        command: "pnpm run build",
        output: "dist"
      },
      environment: {
        VITE_API_BASE_URL: $dev ? "http://localhost:3000" : api.url
      },
      domain: $dev ? undefined : ($app.stage === "production"
        ? "filter-ical.de"
        : `${$app.stage}.filter-ical.de`),
      errorPage: "redirect_to_index",

      dev: {
        command: "pnpm run dev",
        url: "http://localhost:8000"
      }
    });

    return {
      frontend: frontend.url,
      api: api.url || "http://localhost:3000",
      table: table.name,
      syncFunction: syncFunction.arn,
    };
  },
});
