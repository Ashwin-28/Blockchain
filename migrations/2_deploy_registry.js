const BiometricRegistry = artifacts.require("BiometricRegistry");

module.exports = function (deployer) {
  deployer.deploy(BiometricRegistry);
};
