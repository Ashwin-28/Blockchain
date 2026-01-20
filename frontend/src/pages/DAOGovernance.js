import React, { useState, useEffect } from 'react';
import './DAOGovernance.css';

/**
 * DAO Governance Page
 * Decentralized governance for system parameters and protocol upgrades
 */
function DAOGovernance() {
    const [activeTab, setActiveTab] = useState('proposals'); // proposals, voting, treasury
    const [userTokens, setUserTokens] = useState(1250);
    const [votingPower, setVotingPower] = useState(0.05); // 5% of total supply

    const [proposals, setProposals] = useState([
        {
            id: 1,
            title: 'Upgrade to Layer 2 Scaling Solution',
            description: 'Migrate the BiometricRegistry contract to Polygon zkEVM to reduce gas costs by 95% and increase throughput.',
            proposer: '0x742d...35a3',
            status: 'active',
            votesFor: 45000,
            votesAgainst: 12000,
            quorum: 50000,
            endsIn: '2 days',
            category: 'Technical Upgrade'
        },
        {
            id: 2,
            title: 'Add Multi-Signature Requirement for High-Security Enrollments',
            description: 'Require 3-of-5 approval from authorized nodes for enrollments marked as high-security.',
            proposer: '0x8a9b...72c1',
            status: 'active',
            votesFor: 38000,
            votesAgainst: 8000,
            quorum: 50000,
            endsIn: '5 days',
            category: 'Security Enhancement'
        },
        {
            id: 3,
            title: 'Implement GDPR Compliance Module',
            description: 'Add right-to-be-forgotten and data portability features to comply with EU regulations.',
            proposer: '0x1c2d...94f8',
            status: 'pending',
            votesFor: 0,
            votesAgainst: 0,
            quorum: 50000,
            endsIn: 'Not started',
            category: 'Compliance'
        },
        {
            id: 4,
            title: 'Increase Enrollment Center Authorization Threshold',
            description: 'Change the minimum stake required to become an Enrollment Center from 1000 to 5000 tokens.',
            proposer: '0x5e7f...23b9',
            status: 'passed',
            votesFor: 62000,
            votesAgainst: 15000,
            quorum: 50000,
            endsIn: 'Ended',
            category: 'Governance'
        }
    ]);

    const [selectedProposal, setSelectedProposal] = useState(null);
    const [voteChoice, setVoteChoice] = useState(null);

    const treasuryData = {
        totalValue: '$2,450,000',
        tokens: '5,000,000 BIO',
        eth: '450 ETH',
        stablecoins: '$1,200,000 USDC',
        allocations: [
            { name: 'Development Fund', percentage: 40, amount: '$980,000' },
            { name: 'Security Audits', percentage: 25, amount: '$612,500' },
            { name: 'Marketing & Growth', percentage: 20, amount: '$490,000' },
            { name: 'Community Rewards', percentage: 15, amount: '$367,500' }
        ]
    };

    const submitVote = (proposalId, choice) => {
        setProposals(proposals.map(p => {
            if (p.id === proposalId) {
                return {
                    ...p,
                    votesFor: choice === 'for' ? p.votesFor + userTokens : p.votesFor,
                    votesAgainst: choice === 'against' ? p.votesAgainst + userTokens : p.votesAgainst
                };
            }
            return p;
        }));
        setSelectedProposal(null);
        setVoteChoice(null);
    };

    return (
        <div className="page dao-page">
            <div className="container">
                {/* Header */}
                <div className="dao-header fade-up">
                    <div className="mono-label">🏛️ Decentralized Governance</div>
                    <h1>DAO Governance</h1>
                    <p className="dao-subtitle">
                        Participate in decentralized decision-making for the Biometric Identity Protocol.
                        Vote on proposals, manage treasury, and shape the future of the platform.
                    </p>
                </div>

                {/* User Stats */}
                <div className="user-stats fade-up">
                    <div className="stat-card card-glass">
                        <div className="stat-icon">🪙</div>
                        <div className="stat-content">
                            <div className="stat-value">{userTokens.toLocaleString()}</div>
                            <div className="stat-label">BIO Tokens</div>
                        </div>
                    </div>
                    <div className="stat-card card-glass">
                        <div className="stat-icon">⚡</div>
                        <div className="stat-content">
                            <div className="stat-value">{(votingPower * 100).toFixed(2)}%</div>
                            <div className="stat-label">Voting Power</div>
                        </div>
                    </div>
                    <div className="stat-card card-glass">
                        <div className="stat-icon">✓</div>
                        <div className="stat-content">
                            <div className="stat-value">12</div>
                            <div className="stat-label">Votes Cast</div>
                        </div>
                    </div>
                    <div className="stat-card card-glass">
                        <div className="stat-icon">🏆</div>
                        <div className="stat-content">
                            <div className="stat-value">Gold</div>
                            <div className="stat-label">Governance Tier</div>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="dao-tabs fade-up">
                    <button
                        className={`tab-button ${activeTab === 'proposals' ? 'active' : ''}`}
                        onClick={() => setActiveTab('proposals')}
                    >
                        📋 Proposals
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'voting' ? 'active' : ''}`}
                        onClick={() => setActiveTab('voting')}
                    >
                        🗳️ Active Votes
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'treasury' ? 'active' : ''}`}
                        onClick={() => setActiveTab('treasury')}
                    >
                        💰 Treasury
                    </button>
                </div>

                {/* Proposals Tab */}
                {activeTab === 'proposals' && (
                    <div className="proposals-section fade-up">
                        <div className="section-header">
                            <h3>All Proposals</h3>
                            <button className="btn btn-primary">Create Proposal</button>
                        </div>

                        <div className="proposals-list">
                            {proposals.map(proposal => (
                                <div key={proposal.id} className={`proposal-card card ${proposal.status}`}>
                                    <div className="proposal-header">
                                        <div>
                                            <span className={`status-badge ${proposal.status}`}>
                                                {proposal.status.toUpperCase()}
                                            </span>
                                            <span className="category-badge">{proposal.category}</span>
                                        </div>
                                        <div className="proposal-id">#{proposal.id}</div>
                                    </div>

                                    <h4>{proposal.title}</h4>
                                    <p className="proposal-description text-muted">{proposal.description}</p>

                                    <div className="proposal-meta">
                                        <div className="meta-item">
                                            <span className="meta-label">Proposed by</span>
                                            <span className="meta-value">{proposal.proposer}</span>
                                        </div>
                                        <div className="meta-item">
                                            <span className="meta-label">Ends in</span>
                                            <span className="meta-value">{proposal.endsIn}</span>
                                        </div>
                                    </div>

                                    {proposal.status === 'active' && (
                                        <>
                                            <div className="vote-progress">
                                                <div className="progress-labels">
                                                    <span className="for-label">For: {proposal.votesFor.toLocaleString()}</span>
                                                    <span className="against-label">Against: {proposal.votesAgainst.toLocaleString()}</span>
                                                </div>
                                                <div className="progress-bar-dual">
                                                    <div
                                                        className="progress-for"
                                                        style={{ width: `${(proposal.votesFor / proposal.quorum) * 100}%` }}
                                                    ></div>
                                                    <div
                                                        className="progress-against"
                                                        style={{ width: `${(proposal.votesAgainst / proposal.quorum) * 100}%` }}
                                                    ></div>
                                                </div>
                                                <div className="quorum-indicator">
                                                    Quorum: {proposal.quorum.toLocaleString()} votes required
                                                </div>
                                            </div>

                                            <button
                                                className="btn btn-outline mt-md"
                                                onClick={() => setSelectedProposal(proposal)}
                                            >
                                                Vote on Proposal
                                            </button>
                                        </>
                                    )}

                                    {proposal.status === 'passed' && (
                                        <div className="proposal-result success">
                                            ✓ Proposal Passed - Implementation in progress
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Voting Tab */}
                {activeTab === 'voting' && (
                    <div className="voting-section fade-up">
                        <h3>Active Voting Sessions</h3>
                        <div className="active-votes">
                            {proposals.filter(p => p.status === 'active').map(proposal => (
                                <div key={proposal.id} className="vote-card card-glass">
                                    <h4>{proposal.title}</h4>
                                    <div className="vote-stats">
                                        <div className="vote-stat">
                                            <div className="vote-count text-gold">{proposal.votesFor.toLocaleString()}</div>
                                            <div className="vote-label">For</div>
                                        </div>
                                        <div className="vote-divider"></div>
                                        <div className="vote-stat">
                                            <div className="vote-count" style={{ color: 'var(--accent-ruby)' }}>
                                                {proposal.votesAgainst.toLocaleString()}
                                            </div>
                                            <div className="vote-label">Against</div>
                                        </div>
                                    </div>
                                    <button
                                        className="btn btn-primary mt-lg"
                                        onClick={() => setSelectedProposal(proposal)}
                                    >
                                        Cast Your Vote
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Treasury Tab */}
                {activeTab === 'treasury' && (
                    <div className="treasury-section fade-up">
                        <div className="treasury-overview">
                            <div className="treasury-total card-glass">
                                <h3>Total Treasury Value</h3>
                                <div className="treasury-value">{treasuryData.totalValue}</div>
                                <div className="treasury-breakdown">
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">BIO Tokens</span>
                                        <span className="breakdown-value">{treasuryData.tokens}</span>
                                    </div>
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">ETH</span>
                                        <span className="breakdown-value">{treasuryData.eth}</span>
                                    </div>
                                    <div className="breakdown-item">
                                        <span className="breakdown-label">Stablecoins</span>
                                        <span className="breakdown-value">{treasuryData.stablecoins}</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <h3 className="mt-2xl mb-lg">Treasury Allocations</h3>
                        <div className="allocations-grid">
                            {treasuryData.allocations.map((allocation, idx) => (
                                <div key={idx} className="allocation-card card">
                                    <h4>{allocation.name}</h4>
                                    <div className="allocation-percentage">{allocation.percentage}%</div>
                                    <div className="allocation-amount text-gold">{allocation.amount}</div>
                                    <div className="allocation-bar">
                                        <div
                                            className="allocation-fill"
                                            style={{ width: `${allocation.percentage}%` }}
                                        ></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Vote Modal */}
                {selectedProposal && (
                    <div className="vote-modal-overlay" onClick={() => setSelectedProposal(null)}>
                        <div className="vote-modal card-glass" onClick={(e) => e.stopPropagation()}>
                            <h3>Cast Your Vote</h3>
                            <h4 className="mt-md">{selectedProposal.title}</h4>
                            <p className="text-muted mt-sm">{selectedProposal.description}</p>

                            <div className="vote-power-info mt-xl">
                                <span>Your Voting Power:</span>
                                <span className="text-gold">{userTokens.toLocaleString()} votes</span>
                            </div>

                            <div className="vote-options mt-xl">
                                <button
                                    className={`vote-option ${voteChoice === 'for' ? 'selected' : ''}`}
                                    onClick={() => setVoteChoice('for')}
                                >
                                    <div className="option-icon">✓</div>
                                    <div className="option-label">Vote For</div>
                                </button>
                                <button
                                    className={`vote-option ${voteChoice === 'against' ? 'selected' : ''}`}
                                    onClick={() => setVoteChoice('against')}
                                >
                                    <div className="option-icon">✗</div>
                                    <div className="option-label">Vote Against</div>
                                </button>
                            </div>

                            <div className="button-group mt-xl">
                                <button
                                    className="btn btn-outline"
                                    onClick={() => {
                                        setSelectedProposal(null);
                                        setVoteChoice(null);
                                    }}
                                >
                                    Cancel
                                </button>
                                <button
                                    className="btn btn-primary"
                                    disabled={!voteChoice}
                                    onClick={() => submitVote(selectedProposal.id, voteChoice)}
                                >
                                    Submit Vote
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default DAOGovernance;
