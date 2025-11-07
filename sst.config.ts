/// <reference path="./.sst/platform/config.d.ts" />

/**
 * Filter-iCal SST Configuration - Full Serverless Architecture
 *
 * Stack:
 * - Frontend: Vue 3 SPA on CloudFront + S3
 * - Backend: FastAPI on ECS Fargate
 * - API: API Gateway HTTP API with VPC Link (instead of Load Balancer)
 * - Database: PostgreSQL on RDS (t4g.micro, Single-AZ)
 * - Cache: Redis removed (graceful degradation built-in)
 *
 * Cost (eu-north-1):
 * - Fargate: $9/month
 * - RDS t4g.micro: $12.41/month
 * - API Gateway: $1/month (1M requests)
 * - CloudFront + S3: $2/month
 * Total: ~$24/month
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
    // 1. VPC (required for both RDS and Fargate)
    const vpc = new sst.aws.Vpc("FilterIcalVpc");

    // 2. PostgreSQL Database (RDS)
    const database = new sst.aws.Postgres("FilterIcalDB", {
      vpc,
      instance: "t4g.micro",
      version: "16.10",
    });

    // 3. ECS Cluster (for Fargate)
    const cluster = new sst.aws.Cluster("FilterIcalCluster", { vpc });

    // 4. Backend API (FastAPI on ECS Fargate)
    const backend = new sst.aws.Service("FilterIcalBackend", {
      cluster,
      // Docker image configuration
      image: {
        context: "backend",
      },

      // Link to database (automatically injects DATABASE_URL)
      link: [database],

      // Environment variables
      environment: {
        // Stage
        ENVIRONMENT: $app.stage,

        // Dev mode: Secrets from backend/.env.development (no AWS needed, works offline)
        // Deployed: Secrets from AWS Secrets Manager (secure, audited, managed)
        // This pattern allows local dev without per-developer secret setup
        ...($dev ? {} : {
          JWT_SECRET_KEY: new sst.Secret("JwtSecretKey").value,
          SMTP_HOST: new sst.Secret("SmtpHost").value,
          SMTP_PORT: new sst.Secret("SmtpPort").value,
          SMTP_USERNAME: new sst.Secret("SmtpUsername").value,
          SMTP_PASSWORD: new sst.Secret("SmtpPassword").value,
        }),

        // Database URL is auto-injected by SST from 'link: [database]'
        // No need to manually set DATABASE_URL

        // Redis removed - graceful degradation already implemented
        // See backend/app/core/redis.py lines 68-69, 97-98
      },

      // Service discovery via CloudMap (for API Gateway VPC Link)
      // Only needed when deploying, not in dev mode
      ...($dev ? {} : {
        serviceRegistry: {
          port: 3000,
        },
      }),

      // Resource limits
      cpu: "0.25 vCPU",
      memory: "0.5 GB",

      // Auto-scaling
      scaling: {
        min: 1,
        max: 4,
        cpuUtilization: 70,
        memoryUtilization: 80
      },

      // Dev mode configuration (runs backend locally)
      dev: {
        command: ". venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 3000",
        directory: "backend",
        url: "http://localhost:3000"
      }
    });

    // 5. API Gateway (public access to backend via VPC Link)
    // In dev mode, API Gateway is not needed (frontend talks to localhost:3000)
    let api;
    if (!$dev) {
      api = new sst.aws.ApiGatewayV2("FilterIcalBackendApi", {
        vpc,
        domain: $app.stage === "production"
          ? "api.filter-ical.de"
          : `api-${$app.stage}.filter-ical.de`,
      });

      // Private route to backend via CloudMap
      api.routePrivate("$default", backend.nodes.cloudmapService.arn);
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
      domain: $app.stage === "production"
        ? "filter-ical.de"
        : `${$app.stage}.filter-ical.de`,
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
      api: api?.url || "http://localhost:3000",
      database: database.host,
      databasePort: database.port,
      databaseName: database.database,
    };
  },
});
