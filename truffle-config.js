/**
 * Truffle Configuration
 * Decentralized Biometric Identity Verification System
 */

require("dotenv").config();
const HDWalletProvider = require("@truffle/hdwallet-provider");

const MNEMONIC = process.env.MNEMONIC || "";
const INFURA_PROJECT_ID = process.env.INFURA_PROJECT_ID || "";
const ETHERSCAN_API_KEY = process.env.ETHERSCAN_API_KEY || "";

module.exports = {
  contracts_directory: "./contracts",
  contracts_build_directory: "./build/contracts",

  networks: {
    // Local development (Ganache CLI)
    development: {
      host: "127.0.0.1",
      port: 8545,
      network_id: "*",
      gas: 6721975,
      gasPrice: 20000000000,
    },

    // Ganache GUI
    ganache: {
      host: "127.0.0.1",
      port: 7545,
      network_id: 5777,
      gas: 6721975,
    },

    // Sepolia Testnet
    sepolia: {
      provider: () =>
        new HDWalletProvider(
          MNEMONIC,
          `https://sepolia.infura.io/v3/${INFURA_PROJECT_ID}`
        ),
      network_id: 11155111,
      gas: 5500000,
      gasPrice: 20000000000,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true,
    },

    // Ethereum Mainnet
    mainnet: {
      provider: () =>
        new HDWalletProvider(
          MNEMONIC,
          `https://mainnet.infura.io/v3/${INFURA_PROJECT_ID}`
        ),
      network_id: 1,
      gas: 5500000,
      gasPrice: 50000000000,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: false,
    },

    // Polygon Mainnet
    polygon: {
      provider: () =>
        new HDWalletProvider(
          MNEMONIC,
          `https://polygon-mainnet.infura.io/v3/${INFURA_PROJECT_ID}`
        ),
      network_id: 137,
      gas: 6000000,
      gasPrice: 50000000000,
      confirmations: 2,
      timeoutBlocks: 200,
      skipDryRun: true,
    },
  },

  mocha: {
    timeout: 100000,
    useColors: true,
    reporter: "spec",
  },

  compilers: {
    solc: {
      version: "0.8.20",
      settings: {
        optimizer: {
          enabled: true,
          runs: 200,
        },
        evmVersion: "paris",
      },
    },
  },

  plugins: ["truffle-plugin-verify"],

  api_keys: {
    etherscan: ETHERSCAN_API_KEY,
    polygonscan: process.env.POLYGONSCAN_API_KEY || "",
  },

  db: {
    enabled: false,
  },
};
