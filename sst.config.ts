/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "filter-ical",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
      providers: {
        // TEMPORARY: Using student AWS account (310829530903) until filter-ical verification completes
        // TODO: Switch back to "filter-ical" profile after AWS account verification
        aws: {
          region: "eu-north-1",
          profile: "student"
        }
      }
    };
  },
  async run() {
    // Backend API on EC2 (filter-ical account)
    // Using existing DNS records that point to EC2 directly
    // HTTPS configured with Let's Encrypt
    const backendUrl = $app.stage === "production"
      ? "https://api.filter-ical.de"
      : "https://api-staging.filter-ical.de";

    // Frontend (Vue 3 SPA)
    // PHASE 1: Deploy without custom domain (will add DNS in Phase 2)
    const frontend = new sst.aws.StaticSite("FilterIcalFrontend", {
      path: "frontend",
      build: {
        command: "npm run build",
        output: "dist"
      },
      environment: {
        VITE_API_BASE_URL: backendUrl
      },
      // Domain configuration removed for Phase 1 deployment
      // Will add CNAME manually in Route53 after testing CloudFront URL
      errorPage: "redirect_to_index"
    });

    return {
      frontend: frontend.url,
      api: backendUrl
    };
  },
});
