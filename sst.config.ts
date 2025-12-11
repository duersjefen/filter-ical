/// <reference path="./.sst/platform/config.d.ts" />

/**
 * Filter-iCal SST Configuration - True Serverless Architecture
 *
 * Stack:
 * - Frontend: Vue 3 SPA on CloudFront + S3
 * - Backend: FastAPI on AWS Lambda (Python 3.12)
 * - API: API Gateway HTTP API (direct Lambda integration)
 * - Database: DynamoDB (on-demand, serverless)
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
    // Define secrets ONCE at the top
    const jwtSecret = new sst.Secret("JwtSecretKey");
    const adminEmail = new sst.Secret("AdminEmail");
    const adminPassword = new sst.Secret("AdminPassword");

    // 1. DynamoDB Table (single-table design)
    const table = new sst.aws.Dynamo("FilterIcalTable", {
      fields: {
        PK: "string",
        SK: "string",
        link_uuid: "string",
      },
      primaryIndex: { hashKey: "PK", rangeKey: "SK" },
      globalIndexes: {
        LinkUuidIndex: { hashKey: "link_uuid" },
      },
      billing: "on-demand",
    });

    // Shared environment for both Lambda functions
    const sharedEnv = {
      DYNAMODB_TABLE_NAME: table.name,
      ENVIRONMENT: $dev ? "development" : $app.stage,
      IS_LAMBDA: "true",
      USE_DYNAMODB: "true",
      JWT_SECRET_KEY: jwtSecret.value,
      ADMIN_EMAIL: adminEmail.value,
      ADMIN_PASSWORD: adminPassword.value,
    };

    // Shared permissions
    const sharedPermissions = [
      {
        actions: ["ses:SendEmail", "ses:SendRawEmail"],
        resources: ["arn:aws:ses:eu-north-1:*:identity/*"]
      }
    ];

    // 2. Backend API Lambda Function
    const backendFunction = new sst.aws.Function("FilterIcalBackendApi", {
      handler: "backend/app/lambda_handler.handler",
      runtime: "python3.12",
      architecture: "x86_64",
      timeout: "30 seconds",
      memory: "512 MB",
      link: [table],
      environment: sharedEnv,
      permissions: sharedPermissions,
      copyFiles: [
        { from: "backend", to: "backend" },
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

    api.route("ANY /{proxy+}", backendFunction.arn);
    api.route("ANY /", backendFunction.arn);

    // 4. Scheduled Sync Lambda Function
    const syncFunction = new sst.aws.Function("FilterIcalSyncTask", {
      handler: "backend/app/lambda_sync.handler",
      runtime: "python3.12",
      architecture: "x86_64",
      timeout: "5 minutes",
      memory: "512 MB",
      link: [table],
      environment: sharedEnv,
      permissions: sharedPermissions,
      copyFiles: [
        { from: "backend", to: "backend" },
      ],
    });

    // 5. EventBridge Schedule (runs every 30 minutes)
    new sst.aws.Cron("FilterIcalSyncSchedule", {
      schedule: "rate(30 minutes)",
      job: syncFunction,
    });

    // 6. Frontend (Vue 3 SPA on CloudFront + S3)
    const frontend = new sst.aws.StaticSite("FilterIcalFrontend", {
      path: "frontend",
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
    });

    return {
      frontend: frontend.url,
      api: api.url || "http://localhost:3000",
      table: table.name,
    };
  },
});
