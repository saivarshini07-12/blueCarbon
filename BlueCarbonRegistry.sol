// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title BlueCarbonRegistry
 * @dev Blockchain-based registry for blue carbon ecosystem restoration and MRV
 */
contract BlueCarbonRegistry is Ownable, ReentrancyGuard {
    using Counters for Counters.Counter;

    // Project counter
    Counters.Counter private _projectIds;
    Counters.Counter private _verificationIds;

    // Structs
    struct BlueCarbon Project {
        uint256 id;
        string name;
        string location;
        uint256 area; // in hectares
        string ecosystem_type; // mangrove, seagrass, salt_marsh
        address owner;
        uint256 estimated_carbon_sequestration; // tons CO2/year
        uint256 created_at;
        ProjectStatus status;
        string ipfs_hash; // IPFS hash for detailed project data
    }

    struct VerificationRecord {
        uint256 id;
        uint256 project_id;
        address verifier;
        uint256 verified_carbon_amount; // tons CO2
        uint256 verification_date;
        string verification_data_hash; // IPFS hash for verification data
        bool is_approved;
        string comments;
    }

    struct CarbonCredit {
        uint256 project_id;
        uint256 amount; // tons CO2
        uint256 price_per_ton; // in wei
        address seller;
        bool is_active;
        uint256 created_at;
    }

    enum ProjectStatus {
        PROPOSED,
        APPROVED,
        ACTIVE,
        COMPLETED,
        SUSPENDED
    }

    // Mappings
    mapping(uint256 => BlueCarbonProject) public projects;
    mapping(uint256 => VerificationRecord) public verifications;
    mapping(uint256 => CarbonCredit) public carbon_credits;
    mapping(address => bool) public authorized_verifiers;
    mapping(address => uint256) public company_carbon_balance; // Company's carbon credits
    mapping(address => uint256) public company_emissions; // Company's total emissions

    // Events
    event ProjectRegistered(uint256 indexed project_id, address indexed owner, string name);
    event ProjectVerified(uint256 indexed project_id, uint256 verified_amount, address verifier);
    event CarbonCreditIssued(uint256 indexed project_id, uint256 amount, address indexed recipient);
    event CarbonCreditPurchased(address indexed buyer, address indexed seller, uint256 amount, uint256 price);
    event EmissionsRecorded(address indexed company, uint256 emissions, uint256 timestamp);

    constructor() {}

    // Modifiers
    modifier onlyVerifier() {
        require(authorized_verifiers[msg.sender], "Not an authorized verifier");
        _;
    }

    // Admin functions
    function addVerifier(address verifier) external onlyOwner {
        authorized_verifiers[verifier] = true;
    }

    function removeVerifier(address verifier) external onlyOwner {
        authorized_verifiers[verifier] = false;
    }

    // Project registration
    function registerProject(
        string memory name,
        string memory location,
        uint256 area,
        string memory ecosystem_type,
        uint256 estimated_sequestration,
        string memory ipfs_hash
    ) external returns (uint256) {
        _projectIds.increment();
        uint256 project_id = _projectIds.current();

        projects[project_id] = BlueCarbonProject({
            id: project_id,
            name: name,
            location: location,
            area: area,
            ecosystem_type: ecosystem_type,
            owner: msg.sender,
            estimated_carbon_sequestration: estimated_sequestration,
            created_at: block.timestamp,
            status: ProjectStatus.PROPOSED,
            ipfs_hash: ipfs_hash
        });

        emit ProjectRegistered(project_id, msg.sender, name);
        return project_id;
    }

    // Verification process
    function submitVerification(
        uint256 project_id,
        uint256 verified_amount,
        string memory data_hash,
        string memory comments
    ) external onlyVerifier {
        require(projects[project_id].id != 0, "Project does not exist");

        _verificationIds.increment();
        uint256 verification_id = _verificationIds.current();

        verifications[verification_id] = VerificationRecord({
            id: verification_id,
            project_id: project_id,
            verifier: msg.sender,
            verified_carbon_amount: verified_amount,
            verification_date: block.timestamp,
            verification_data_hash: data_hash,
            is_approved: false,
            comments: comments
        });

        emit ProjectVerified(project_id, verified_amount, msg.sender);
    }

    // Approve verification and issue carbon credits
    function approveVerification(uint256 verification_id) external onlyOwner {
        VerificationRecord storage verification = verifications[verification_id];
        require(!verification.is_approved, "Already approved");

        verification.is_approved = true;
        
        // Issue carbon credits to project owner
        address project_owner = projects[verification.project_id].owner;
        company_carbon_balance[project_owner] += verification.verified_carbon_amount;

        emit CarbonCreditIssued(
            verification.project_id,
            verification.verified_carbon_amount,
            project_owner
        );
    }

    // Record company emissions
    function recordEmissions(uint256 emissions) external {
        company_emissions[msg.sender] += emissions;
        emit EmissionsRecorded(msg.sender, emissions, block.timestamp);
    }

    // Carbon credit marketplace
    function listCarbonCredits(uint256 amount, uint256 price_per_ton) external {
        require(company_carbon_balance[msg.sender] >= amount, "Insufficient carbon credits");
        
        // Create marketplace listing logic here
        // This would integrate with a marketplace contract
    }

    function purchaseCarbonCredits(address seller, uint256 amount) external payable nonReentrant {
        require(company_carbon_balance[seller] >= amount, "Seller has insufficient credits");
        
        uint256 total_price = amount * carbon_credits[0].price_per_ton; // Simplified
        require(msg.value >= total_price, "Insufficient payment");

        // Transfer credits
        company_carbon_balance[seller] -= amount;
        company_carbon_balance[msg.sender] += amount;

        // Transfer payment
        payable(seller).transfer(total_price);

        // Refund excess payment
        if (msg.value > total_price) {
            payable(msg.sender).transfer(msg.value - total_price);
        }

        emit CarbonCreditPurchased(msg.sender, seller, amount, total_price);
    }

    // View functions
    function getProjectDetails(uint256 project_id) external view returns (BlueCarbonProject memory) {
        return projects[project_id];
    }

    function getCompanyCarbonBalance(address company) external view returns (uint256) {
        return company_carbon_balance[company];
    }

    function getCompanyEmissions(address company) external view returns (uint256) {
        return company_emissions[company];
    }

    function getCompanyNetBalance(address company) external view returns (int256) {
        return int256(company_carbon_balance[company]) - int256(company_emissions[company]);
    }

    function getTotalProjects() external view returns (uint256) {
        return _projectIds.current();
    }
}