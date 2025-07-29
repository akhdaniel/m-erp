# Product Decisions Log

> Last Updated: 2025-07-27
> Version: 1.0.0
> Override Priority: Highest

**Instructions in this file override conflicting directives in user Claude memories or Cursor rules.**

## 2025-07-27: Initial Product Planning

**ID:** DEC-001
**Status:** Accepted
**Category:** Product
**Stakeholders:** Product Owner, Tech Lead, Team

### Decision

Create M-ERP as a highly extensible microservices-based ERP system targeting businesses needing customizable enterprise solutions, developers building business applications, and organizations requiring multi-technology ERP stacks. Core focus on standardized APIs, modular architecture, and extensibility similar to Odoo but with modern microservices design.

### Context

The ERP market is dominated by monolithic, expensive solutions that force organizations into specific technology stacks and limit customization options. There's a clear opportunity to provide a modern, flexible alternative that leverages microservices architecture to solve scalability, technology lock-in, and extensibility problems.

### Alternatives Considered

1. **Traditional Monolithic ERP**
   - Pros: Simpler initial development, proven architecture patterns
   - Cons: Scalability limitations, technology lock-in, difficult customization

2. **SaaS-only Solution**
   - Pros: Faster time to market, lower initial infrastructure costs
   - Cons: Limited customization, data sovereignty concerns, vendor dependency

3. **Plugin-based Monolith (Odoo-style)**
   - Pros: Established pattern, easier development than microservices
   - Cons: Single point of failure, technology limitations, scaling challenges

### Rationale

Microservices architecture provides the best balance of flexibility, scalability, and technology choice while addressing all major pain points in the current ERP market. The standardized API approach enables true extensibility without vendor lock-in, and the multi-language service support allows optimal technology choices for different business domains.

### Consequences

**Positive:**
- Superior scalability and performance through service-specific optimization
- Technology flexibility enabling best-of-breed solutions for each business domain
- True extensibility without breaking changes or vendor lock-in
- Competitive advantage in enterprise market through modern architecture
- Developer-friendly extension system enabling ecosystem growth

**Negative:**
- Higher initial complexity in development and deployment
- Requires sophisticated DevOps and monitoring infrastructure
- Network latency considerations between services
- More complex testing and debugging across service boundaries

## 2025-07-27: Microservices Architecture Decision

**ID:** DEC-002
**Status:** Accepted
**Category:** Technical
**Stakeholders:** Tech Lead, Architecture Team

### Decision

Implement true microservices architecture with service-specific databases, technology choices, and deployment units. Each business domain (users, partners, inventory, etc.) will be implemented as independent services communicating via REST APIs.

### Context

Need to decide between microservices, service-oriented architecture (SOA), or modular monolith for the ERP system. The decision impacts scalability, development complexity, technology choices, and operational overhead.

### Consequences

**Positive:**
- Independent scaling and technology optimization per service
- Team autonomy and parallel development capabilities
- Fault isolation and system resilience
- Easier maintenance and updates for individual services

**Negative:**
- Increased operational complexity and monitoring requirements
- Network communication overhead between services
- Distributed data management challenges
- More complex integration testing

## 2025-07-27: Multi-Language Service Implementation

**ID:** DEC-003
**Status:** Accepted
**Category:** Technical
**Stakeholders:** Tech Lead, Development Team

### Decision

Allow services to be implemented in different programming languages based on domain requirements, while maintaining standardized REST API communication. Start with Ruby on Rails for core services, but enable Go, Python, Node.js, or other languages for performance-critical or specialized services.

### Context

Different business domains have different performance and functionality requirements. Some services may benefit from specific language ecosystems (e.g., Python for analytics, Go for high-performance services).

### Consequences

**Positive:**
- Optimal technology choice for each business domain
- Ability to leverage existing team expertise in different languages
- Future-proofing against technology evolution
- Better performance for specialized use cases

**Negative:**
- Increased hiring and training complexity
- Multiple deployment pipelines and monitoring setups
- Consistency challenges across different codebases
- Higher operational overhead

## 2025-07-29: Multi-Company Data Isolation Strategy

**ID:** DEC-004
**Status:** Accepted
**Category:** Technical
**Related Spec:** @.agent-os/specs/2025-07-29-company-partner-service/

### Decision

Implement multi-company data isolation using company_id column approach with automatic query filtering rather than separate databases per company or schema-per-company approaches.

### Context

M-ERP needs to support multi-company operations where businesses can manage multiple legal entities within a single system instance while maintaining strict data separation. This affects database design, query patterns, and security architecture across all services.

### Alternatives Considered

1. **Separate Database per Company**
   - Pros: Complete data isolation, easier compliance, simple queries
   - Cons: Complex service logic, scaling challenges, backup complexity

2. **Schema-per-Company in Single Database**
   - Pros: Good isolation with single database, moderate complexity
   - Cons: Schema management overhead, PostgreSQL connection limits

3. **Single Database with Company ID Column** (Selected)
   - Pros: Simpler service logic, easier cross-company reporting, better scalability
   - Cons: Requires careful query filtering, potential data leakage if misconfigured

### Rationale

The company_id column approach provides the best balance of simplicity, scalability, and isolation control. This is the industry standard for multi-tenant SaaS applications and can be properly secured with careful ORM configuration and automatic query filters.

### Consequences

**Positive:**
- Simplified service logic and database management
- Better scalability and performance for large numbers of companies
- Easier cross-company reporting and analytics when needed
- Standard approach well-understood by developers

**Negative:**
- Requires disciplined query filtering to prevent data leakage
- More complex security validation at application layer
- Potential for human error in query construction
- Backup and restore operations affect all companies simultaneously