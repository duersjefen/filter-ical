/// <reference path="./.sst/platform/config.d.ts" />

export default $config({
  app(input) {
    return {
      name: "filter-ical",
      removal: input?.stage === "production" ? "retain" : "remove",
      home: "aws",
      providers: {
        // Using NEW filter-ical AWS account (165046687980)
        aws: {
          region: "eu-north-1",
          profile: "filter-ical"
        }
      }
    };
  },
  async run() {
    // Backend API URL (EC2 instance - already deployed)
    const backendUrl = $app.stage === "production"
      ? "https://api.filter-ical.de"
      : "https://api-staging.filter-ical.de";

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
            name: "filter-ical.de",
            dns: sst.aws.dns()
          }
        : {
            name: "staging.filter-ical.de",
            dns: sst.aws.dns()
          },
      errorPage: "redirect_to_index"
    });

    return {
      frontend: frontend.url,
      backendUrl: backendUrl
    };
  },
});
