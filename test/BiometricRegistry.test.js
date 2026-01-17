const BiometricRegistry = artifacts.require("BiometricRegistry");
const { expectEvent, expectRevert } = require("@openzeppelin/test-helpers");
const { expect } = require("chai");

contract("BiometricRegistry", (accounts) => {
  const [owner, enrollmentCenter, authCenter, user1, user2] = accounts;
  let registry;

  beforeEach(async () => {
    registry = await BiometricRegistry.new({ from: owner });
  });

  describe("Deployment", () => {
    it("should set the deployer as owner", async () => {
      const contractOwner = await registry.owner();
      expect(contractOwner).to.equal(owner);
    });

    it("should register deployer as Main Enrollment Center", async () => {
      const isEC = await registry.isEnrollmentCenter(owner);
      expect(isEC).to.be.true;
    });

    it("should initialize with 1 node and 0 subjects", async () => {
      const totalNodes = await registry.totalNodes();
      const totalSubjects = await registry.totalSubjects();
      expect(totalNodes.toNumber()).to.equal(1);
      expect(totalSubjects.toNumber()).to.equal(0);
    });
  });

  describe("Node Registration", () => {
    it("should allow EC to register new nodes", async () => {
      const tx = await registry.registerNode(
        enrollmentCenter,
        "Test Enrollment Center",
        true,
        { from: owner }
      );

      expectEvent(tx, "NodeRegistered", {
        nodeAddress: enrollmentCenter,
        isEnrollmentCenter: true
      });

      const isEC = await registry.isEnrollmentCenter(enrollmentCenter);
      expect(isEC).to.be.true;
    });

    it("should reject node registration from non-EC", async () => {
      await expectRevert(
        registry.registerNode(authCenter, "Test AC", false, { from: user1 }),
        "BiometricRegistry: not an enrollment center"
      );
    });
  });

  describe("Subject Enrollment", () => {
    const subjectId = web3.utils.soliditySha3("subject1");
    const commitmentHash = web3.utils.soliditySha3("commitment1");
    const delta = web3.utils.soliditySha3("delta1");
    const templateCID = "QmTestHash123";

    it("should allow EC to enroll subjects", async () => {
      const tx = await registry.enrollSubject(
        subjectId,
        commitmentHash,
        delta,
        templateCID,
        0, // FACIAL
        { from: owner }
      );

      expectEvent(tx, "SubjectEnrolled", {
        subjectId: subjectId,
        enrolledBy: owner
      });

      const totalSubjects = await registry.totalSubjects();
      expect(totalSubjects.toNumber()).to.equal(1);
    });

    it("should reject duplicate subject enrollment", async () => {
      await registry.enrollSubject(
        subjectId,
        commitmentHash,
        delta,
        templateCID,
        0,
        { from: owner }
      );

      await expectRevert(
        registry.enrollSubject(
          subjectId,
          commitmentHash,
          delta,
          templateCID,
          0,
          { from: owner }
        ),
        "BiometricRegistry: subject already exists"
      );
    });

    it("should reject enrollment from non-EC", async () => {
      await expectRevert(
        registry.enrollSubject(
          subjectId,
          commitmentHash,
          delta,
          templateCID,
          0,
          { from: user1 }
        ),
        "BiometricRegistry: not an enrollment center"
      );
    });
  });

  describe("Authentication", () => {
    const subjectId = web3.utils.soliditySha3("authSubject");
    const commitmentHash = web3.utils.soliditySha3("authCommitment");
    const delta = web3.utils.soliditySha3("authDelta");

    beforeEach(async () => {
      // Register an AC
      await registry.registerNode(authCenter, "Auth Center", false, { from: owner });
      
      // Enroll a subject
      await registry.enrollSubject(
        subjectId,
        commitmentHash,
        delta,
        "QmTestCID",
        0,
        { from: owner }
      );
    });

    it("should allow AC to verify commitment", async () => {
      const isValid = await registry.verifyCommitment(
        subjectId,
        commitmentHash,
        { from: authCenter }
      );
      expect(isValid).to.be.true;
    });

    it("should reject invalid commitment", async () => {
      const wrongHash = web3.utils.soliditySha3("wrongHash");
      const isValid = await registry.verifyCommitment(
        subjectId,
        wrongHash,
        { from: authCenter }
      );
      expect(isValid).to.be.false;
    });

    it("should log authentication attempts", async () => {
      const tx = await registry.logAuthentication(
        subjectId,
        true,
        "Verification successful",
        { from: authCenter }
      );

      expectEvent(tx, "AuthenticationLogged", {
        subjectId: subjectId,
        verifier: authCenter,
        success: true
      });

      const totalLogs = await registry.totalAuthRecords();
      expect(totalLogs.toNumber()).to.equal(1);
    });
  });

  describe("Subject Management", () => {
    const subjectId = web3.utils.soliditySha3("manageSubject");
    const commitmentHash = web3.utils.soliditySha3("manageCommitment");
    const delta = web3.utils.soliditySha3("manageDelta");

    beforeEach(async () => {
      await registry.registerNode(authCenter, "Auth Center", false, { from: owner });
      await registry.enrollSubject(
        subjectId,
        commitmentHash,
        delta,
        "QmCID",
        0,
        { from: owner }
      );
    });

    it("should deactivate subject", async () => {
      await registry.deactivateSubject(subjectId, { from: owner });
      
      const [exists, isActive] = await registry.checkSubjectStatus(subjectId);
      expect(exists).to.be.true;
      expect(isActive).to.be.false;
    });

    it("should reactivate subject", async () => {
      await registry.deactivateSubject(subjectId, { from: owner });
      await registry.reactivateSubject(subjectId, { from: owner });
      
      const [exists, isActive] = await registry.checkSubjectStatus(subjectId);
      expect(exists).to.be.true;
      expect(isActive).to.be.true;
    });
  });
});
