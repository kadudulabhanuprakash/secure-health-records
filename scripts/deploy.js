// File: scripts/deploy.js
const { ethers } = require("hardhat");

async function main() {
  const AccessLogger = await ethers.getContractFactory("AccessLogger");
  const accessLogger = await AccessLogger.deploy();

  await accessLogger.waitForDeployment();

  console.log("AccessLogger deployed to:", await accessLogger.getAddress());

  // Save ABI and address to contracts/AccessLogger.json
  const fs = require("fs");
  const path = require("path");
  const contractsDir = path.join(__dirname, "../contracts");
  if (!fs.existsSync(contractsDir)) {
    fs.mkdirSync(contractsDir, { recursive: true });
  }

  const contractData = {
    address: await accessLogger.getAddress(),
    abi: AccessLogger.interface.formatJson(),
  };
  const jsonPath = path.join(contractsDir, "AccessLogger.json");
  fs.writeFileSync(jsonPath, JSON.stringify(contractData, null, 2));

  console.log("Contract data saved to:", jsonPath);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });