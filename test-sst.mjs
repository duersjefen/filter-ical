// Minimal SST config test
export default {
  async run() {
    console.log("SST run() executed successfully");
    console.log("$dev:", $dev);
    console.log("$app.stage:", $app.stage);
    
    return {
      test: "success"
    };
  }
};
