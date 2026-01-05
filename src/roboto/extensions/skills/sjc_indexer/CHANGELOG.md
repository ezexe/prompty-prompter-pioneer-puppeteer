# Changelog

All notable changes to sjc_indexer extension.

## [0.1.0] - 2026-01-05

### Added
- Initial release
- SJC meta-pattern formula (Specific + Structured + Junction + Counterfactual)
- Three prompt tiers with reliability weights
- Five components: anchor_selector, seam_finder, junction_explorer, boundary_mapper, synthesizer
- Component weight evaluations (consistency, coverage, precision, composability)
- Execution protocol with 5 phases
- Termination conditions
- Output schema for indexed_knowledge_model
- VLDS integration tracking
- Bias risk pattern: sjc_underutilization
- Phase hooks: detect_knowledge_exploration_requests, execute_sjc_protocol, index_domain_knowledge