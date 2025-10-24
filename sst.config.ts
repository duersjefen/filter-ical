/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "filter-ical",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
      providers: {
        // Using NEW AWS account (paiss → filter-ical, same as gabs-massage.de)
        aws: {
          region: "eu-north-1",
          profile: "paiss-filter-ical"
        }
      }
    };
  },
  async run() {
    // Backend API URL (EC2 instance - will be set up separately)
    const backendUrl = $app.stage === "production"
      ? "https://api.paiss.me"  // EC2 backend API
      : "https://api-staging.paiss.me";  // EC2 staging backend API

    // Frontend (Vue 3 SPA)
    const frontend = new sst.aws.StaticSite("FilterIcalFrontend", {
      path: "frontend",
      build: {
        command: "npm run build",
        output: "dist"
      },
      environment: {
        VITE_API_BASE_URL: backendUrl
      },
      domain: $app.stage === "production"
        ? {
            name: "paiss.me",
            redirects: ["www.paiss.me"],
            dns: sst.aws.dns()
          }
        : {
            name: `temp-staging.paiss.me`,
            dns: sst.aws.dns()
          },
      errorPage: "redirect_to_index"  // SPA routing support
    });

    return {
      frontend: frontend.url,
      backendUrl: backendUrl
    };
  },
});
