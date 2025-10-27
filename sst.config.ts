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
    // EC2 Backend Instance (manually managed)
    const ec2IpAddress = "13.50.144.0";
    const productionPort = 3000;
    const stagingPort = 3001;

    // Backend API (CloudFront in front of EC2 for SSL)
    const apiDistribution = new sst.aws.Router("FilterIcalApi", {
      domain: $app.stage === "production"
        ? {
            name: "api.filter-ical.de",
            dns: sst.aws.dns()
          }
        : {
            name: "api-staging.filter-ical.de",
            dns: sst.aws.dns()
          },
      routes: {
        "/*": {
          url: $app.stage === "production"
            ? `http://${ec2IpAddress}:${productionPort}`
            : `http://${ec2IpAddress}:${stagingPort}`
        }
      }
    });

    const backendUrl = apiDistribution.url;

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
      api: backendUrl
    };
  },
});
