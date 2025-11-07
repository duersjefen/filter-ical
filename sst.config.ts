/// <reference path="./.sst/platform/config.d.ts" />

/**
 * Filter-iCal SST Configuration - Full Serverless Architecture
 *
 * Stack:
 * - Frontend: Vue 3 SPA on CloudFront + S3
 * - Backend: FastAPI on AWS Lambda (Python 3.13)
 * - API: API Gateway HTTP API (direct Lambda integration)
 * - Database: PostgreSQL on RDS (t4g.micro, Single-AZ)
 * - Scheduler: EventBridge (30-minute interval for calendar sync)
 *
 * Cost (eu-north-1):
 * - Lambda: $0/month (within free tier)
 * - RDS t4g.micro: $12.41/month
 * - API Gateway: $0/month (within free tier)
 * - CloudFront + S3: $2/month
 * - EventBridge: $0.00/month (negligible)
 * Total: ~$14/month (42% savings vs ECS)
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
          profile: "filter-ical"  // Single AWS account - CloudFront now verified!
        }
      }
    };
  },
  async run() {
    // 1. VPC (required for RDS and Lambda)
    const vpc = new sst.aws.Vpc("FilterIcalVpc");

    // 2. PostgreSQL Database (RDS)
    const database = new sst.aws.Postgres("FilterIcalDB", {
      vpc,
      instance: "t4g.micro",
      version: "16.10",
    });

    // 3. Backend API Lambda Function (FastAPI with Mangum)
    const backendFunction = new sst.aws.Function("FilterIcalBackendApi", {
      vpc,
      handler: "backend/lambda_api.handler",
      runtime: "python3.13",
      timeout: "30 seconds",
      memory: "512 MB",

      // Link to database (automatically injects DATABASE_URL)
      link: [database],

      // Environment variables
      environment: {
        // Stage
        ENVIRONMENT: $app.stage,

        // Lambda execution context flag
        IS_LAMBDA: "true",

        // Dev mode: Secrets from backend/.env.development (no AWS needed, works offline)
        // Deployed: Secrets from AWS Secrets Manager (secure, audited, managed)
        ...($dev ? {} : {
          JWT_SECRET_KEY: new sst.Secret("JwtSecretKey").value,
          SMTP_HOST: new sst.Secret("SmtpHost").value,
          SMTP_PORT: new sst.Secret("SmtpPort").value,
          SMTP_USERNAME: new sst.Secret("SmtpUsername").value,
          SMTP_PASSWORD: new sst.Secret("SmtpPassword").value,
        }),
      },

      // Python build configuration
      python: {
        container: true,  // Use Docker container for dependencies
      },

      // Dev mode configuration (runs backend locally)
      dev: {
        command: ". venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 3000",
        directory: "backend",
        url: "http://localhost:3000"
      },
    });

    // 4. API Gateway with custom domain (wraps Lambda function)
    const api = new sst.aws.ApiGatewayV2("FilterIcalApi", {
      domain: $dev ? undefined : ($app.stage === "production"
        ? "api.filter-ical.de"
        : `api-${$app.stage}.filter-ical.de`),
      cors: {
        allowOrigins: $app.stage === "production"
          ? ["https://filter-ical.de", "https://www.filter-ical.de"]
          : $app.stage === "staging"
          ? ["https://staging.filter-ical.de"]
          : ["*"],
        allowMethods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allowHeaders: ["Content-Type", "Authorization", "Accept", "Accept-Language", "X-Requested-With"],
        allowCredentials: true,
      },
    });

    // Route all requests to backend Lambda
    api.route("ANY /{proxy+}", backendFunction.arn);
    api.route("ANY /", backendFunction.arn);

    // 5. Scheduled Sync Lambda Function
    const syncFunction = new sst.aws.Function("FilterIcalSyncTask", {
      vpc,
      handler: "backend/lambda_sync.handler",
      runtime: "python3.13",
      timeout: "5 minutes",  // Longer timeout for sync operations
      memory: "512 MB",

      // Link to database
      link: [database],

      // Environment variables
      environment: {
        ENVIRONMENT: $app.stage,
        IS_LAMBDA: "true",

        ...($dev ? {} : {
          JWT_SECRET_KEY: new sst.Secret("JwtSecretKey").value,
          SMTP_HOST: new sst.Secret("SmtpHost").value,
          SMTP_PORT: new sst.Secret("SmtpPort").value,
          SMTP_USERNAME: new sst.Secret("SmtpUsername").value,
          SMTP_PASSWORD: new sst.Secret("SmtpPassword").value,
        }),
      },

      python: {
        container: true,
      },
    });

    // 6. EventBridge Scheduler (runs every 30 minutes)
    if (!$dev) {
      new sst.aws.Cron("FilterIcalSyncScheduler", {
        schedule: "rate(30 minutes)",
        job: syncFunction,
      });
    }

    // 6. Frontend (Vue 3 SPA on CloudFront + S3)
    const frontend = new sst.aws.StaticSite("FilterIcalFrontend", {
      path: "frontend",
      build: {
        command: "npm run build",
        output: "dist"
      },
      environment: {
        // In dev mode: talk to local backend, in deployed: use API Gateway
        VITE_API_BASE_URL: $dev ? "http://localhost:3000" : api.url
      },
      // Custom domain for frontend (Route53 auto-managed by SST)
      domain: $dev ? undefined : ($app.stage === "production"
        ? "filter-ical.de"
        : `${$app.stage}.filter-ical.de`),
      errorPage: "redirect_to_index",

      // Dev mode configuration (runs Vite dev server locally)
      dev: {
        command: "npm run dev",
        directory: "frontend",
        url: "http://localhost:5173"
      }
    });

    return {
      frontend: frontend.url,
      api: api.url || "http://localhost:3000",
      database: database.host,
      databasePort: database.port,
      databaseName: database.database,
      syncFunction: syncFunction.arn,
    };
  },
});
