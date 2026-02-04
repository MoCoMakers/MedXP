# Branch Protection Strategy for MedXP

This document outlines the branch protection rules and Git workflow for the MedXP project.

## Branch Structure

### Main Branches

- **main** - Production-ready code, protected
- **develop** - Integration branch for next release, protected
- **feature/*** - Feature branches (created from develop)
- **release/*** - Release preparation branches (created from develop)
- **hotfix/*** - Emergency production fixes (created from main)

### Branch Naming Conventions

```
feature/[issue-id]-[short-description]
release/[version]
hotfix/[issue-id]-[short-description]
```

Examples:
- `feature/123-add-nurse-recording`
- `feature/456-implement-fhir-integration`
- `release/1.0.0`
- `hotfix/789-fix-authentication-bug`

## Branch Protection Rules

### Protected Branches

#### main (Production)
- Required status checks: All CI/CD pipelines must pass
- Required reviews: Minimum 2 approvals
- Require code owner approval: Yes
- Allow force push: No
- Require signed commits: Recommended
- Include administrators: Same protection rules

#### develop (Development Integration)
- Required status checks: All CI pipelines must pass
- Required reviews: Minimum 1 approval
- Require code owner approval: No
- Allow force push: No (via branch protection)
- Require signed commits: No

#### release/* (Release Branches)
- Required status checks: All CI pipelines must pass
- Required reviews: Minimum 2 approvals
- Require code owner approval: Yes
- Allow force push: No
- Deletion after merge: Yes

#### hotfix/* (Emergency Fixes)
- Required status checks: All CI pipelines must pass
- Required reviews: Minimum 1 approval (expedited review)
- Allow direct push: No (except via PR)

## Pull Request Requirements

### Code Review
- All changes must go through Pull Request
- Minimum reviewer count as specified per branch
- Reviewers must be team members with appropriate permissions
- Self-approvals not allowed

### Status Checks
- **Required CI Checks:**
  - Linting (ESLint for JS, Flake8 for Python)
  - Unit tests (coverage > 80%)
  - Security scanning (Bandit, Snyk)
  - Type checking (TypeScript)
  - Build verification

- **Recommended Checks:**
  - Integration tests
  - Performance benchmarks
  - Accessibility checks

### Description Requirements
- Link to related issue/ticket
- Clear description of changes
- Testing instructions
- Screenshots for UI changes
- Breaking changes highlighted

### Merge Strategies

#### squash (Recommended for feature branches)
- Squash all commits into single logical unit
- Keep clean commit history
- Edit commit message during squash

#### rebase (For release branches)
- Maintain linear history
- Clean, organized commit log

#### merge (For release branches only)
- Preserve complete history
- Visualize integration points

## Commit Message Convention

```
type(scope): subject

body (optional)

footer (optional)
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Formatting, no code change
- **refactor**: Code restructuring
- **test**: Adding tests
- **chore**: Maintenance tasks

### Examples
```
feat(auth): add nurse authentication flow

Implement JWT-based authentication with role-based access control.
Nurses can now authenticate using their hospital credentials.

Closes #123
```

```
fix(transcription): resolve audio upload timeout issue

Increased timeout for large audio files (>100MB) from 30s to 120s.
Added chunked upload support for unreliable connections.

Fixes #456
```

## CI/CD Pipeline Integration

### GitHub Actions Workflows

1. **ci.yml** - Run on every PR and push to main/develop
   - Install dependencies
   - Run linters
   - Run unit tests
   - Run security scans
   - Build Docker images

2. **cd.yml** - Run on merge to main
   - Push to container registry
   - Deploy to staging
   - Run integration tests
   - Deploy to production

3. **security.yml** - Scheduled and on PR
   - Dependency vulnerability scanning
   - Secret detection
   - CodeQL analysis

## Release Process

### Version Numbering
Semantic versioning: MAJOR.MINOR.PATCH

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
1. Create release branch from develop
2. Update version numbers
3. Run full test suite
4. Update changelog
5. Create pull request to main
6. After merge, tag the release
7. Delete release branch

## Emergency Hotfix Procedure

1. Create hotfix branch from main
2. Implement fix with minimal changes
3. Create pull request directly to main
4. Expedited review (aim for < 2 hours)
5. Merge and deploy immediately
6. Cherry-pick changes to develop

## Repository Settings Configuration

### GitHub Settings (via Web UI)

1. Go to Repository Settings > Branches
2. Add branch protection rule for "main"
3. Add branch protection rule for "develop"
4. Configure required status checks
5. Configure required reviewers
6. Enable branch auto-deletion on merge

### Required Teams/Users

- **Repository Administrators**: Full access
- **Senior Developers**: Admin or maintainer access
- **Developers**: Write access to feature branches
- **AI/LLM Systems**: Read access for documentation

## Compliance Considerations

### Audit Trail
- All branch protections logged
- Pull request history preserved
- Code review comments retained
- Deployment history tracked

### HIPAA Compliance
- Access controls enforced at branch level
- Sensitive configuration not in repository
- Audit logging enabled for all operations
