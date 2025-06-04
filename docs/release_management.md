# Release Management Process for Eternia

This document outlines the release management process for the Eternia project, including versioning strategy, release workflow, and deployment procedures.

## Versioning Strategy

Eternia follows [Semantic Versioning](https://semver.org/) (SemVer) for version numbering:

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backward-compatible functionality additions
- **PATCH**: Incremented for backward-compatible bug fixes
- **PRERELEASE**: Optional identifier for pre-release versions (e.g., alpha, beta, rc)
- **BUILD**: Optional build metadata

### Examples

- `1.0.0`: Initial stable release
- `1.1.0`: New features added
- `1.1.1`: Bug fixes
- `2.0.0`: Breaking changes
- `1.2.0-alpha.1`: Alpha pre-release
- `1.2.0-beta.2`: Beta pre-release
- `1.2.0-rc.1`: Release candidate

## Release Types

### Regular Releases

Regular releases follow the standard development cycle and are deployed to production after thorough testing.

### Hotfix Releases

Hotfix releases address critical issues in production and follow an expedited process to minimize the time to fix.

### Feature Releases

Feature releases introduce new functionality and follow the standard development cycle.

## Release Workflow

### 1. Release Planning

1. **Feature Selection**: Determine which features and fixes will be included in the release
2. **Version Assignment**: Assign a version number based on the SemVer rules
3. **Timeline Establishment**: Set target dates for code freeze, testing, and release

### 2. Development Phase

1. **Feature Branches**: Develop features in dedicated branches
2. **Pull Requests**: Submit pull requests for code review
3. **Continuous Integration**: Ensure all tests pass for each pull request
4. **Code Review**: Conduct thorough code reviews before merging

### 3. Release Preparation

1. **Release Branch Creation**: Create a release branch from the main branch
   ```bash
   git checkout -b release/v1.2.0 main
   ```

2. **Version Bump**: Update version numbers in relevant files
   ```bash
   # Example: Update package.json
   sed -i 's/"version": "1.1.0"/"version": "1.2.0"/g' ui/package.json
   ```

3. **Changelog Generation**: Generate or update the changelog
   ```bash
   # Using git-cliff or similar tool
   git-cliff --tag v1.2.0 > CHANGELOG.md
   ```

4. **Pre-release Testing**: Deploy to staging environment for testing
   ```bash
   # Trigger staging deployment
   git push origin release/v1.2.0
   ```

### 4. Release Execution

1. **Final Approval**: Obtain approval from stakeholders
2. **Release Tag Creation**: Create and push a git tag for the release
   ```bash
   git tag -a v1.2.0 -m "Release v1.2.0"
   git push origin v1.2.0
   ```

3. **Production Deployment**: Deploy the release to production
   ```bash
   # CI/CD will automatically deploy tagged releases
   ```

4. **Merge Back**: Merge the release branch back to main
   ```bash
   git checkout main
   git merge --no-ff release/v1.2.0
   git push origin main
   ```

### 5. Post-Release

1. **Monitoring**: Monitor application performance and error rates
2. **User Feedback**: Collect and analyze user feedback
3. **Retrospective**: Conduct a release retrospective to identify improvements

## Hotfix Process

1. **Branch Creation**: Create a hotfix branch from the production tag
   ```bash
   git checkout -b hotfix/v1.2.1 v1.2.0
   ```

2. **Fix Implementation**: Implement and test the fix
3. **Version Bump**: Update version numbers (patch increment)
4. **Hotfix Release**: Tag and deploy the hotfix
   ```bash
   git tag -a v1.2.1 -m "Hotfix v1.2.1"
   git push origin v1.2.1
   ```

5. **Merge Back**: Merge the hotfix to both main and the current release branch
   ```bash
   git checkout main
   git merge --no-ff hotfix/v1.2.1
   git push origin main
   ```

## Release Artifacts

Each release generates the following artifacts:

1. **Git Tag**: A tag in the repository marking the release commit
2. **Docker Images**: Tagged Docker images for backend and frontend
   ```
   ghcr.io/username/eternia/backend:v1.2.0
   ghcr.io/username/eternia/frontend:v1.2.0
   ```

3. **Changelog**: Documentation of changes since the previous release
4. **Release Notes**: User-facing description of new features and fixes

## Deployment Strategy

### Staging Deployment

1. **Automatic Deployment**: Every push to a release branch triggers deployment to staging
2. **Environment**: Uses the staging Kubernetes namespace
3. **Testing**: UAT and performance testing are conducted in staging

### Production Deployment

1. **Tag-Based Deployment**: Only tagged releases are deployed to production
2. **Approval Process**: Requires manual approval in the CI/CD pipeline
3. **Rollback Plan**: Includes a documented rollback procedure

## Rollback Procedure

If issues are detected after deployment:

1. **Decision**: Determine whether to fix forward or roll back
2. **Rollback Command**: Execute the rollback
   ```bash
   # Roll back to previous version
   kubectl rollout undo deployment/eternia-backend -n eternia-production
   kubectl rollout undo deployment/eternia-frontend -n eternia-production
   ```

3. **Verification**: Verify the rollback was successful
4. **Communication**: Inform stakeholders of the rollback

## Release Calendar

- **Regular Releases**: Scheduled bi-weekly
- **Feature Releases**: Scheduled monthly
- **Hotfixes**: As needed, with expedited process

## Release Roles and Responsibilities

- **Release Manager**: Coordinates the release process
- **Development Team**: Implements features and fixes
- **QA Team**: Tests the release
- **DevOps Team**: Manages the deployment
- **Product Owner**: Approves the release content

## Release Documentation

For each release, the following documentation is maintained:

1. **Release Plan**: Features, timeline, and responsibilities
2. **Release Notes**: User-facing documentation of changes
3. **Deployment Checklist**: Steps to deploy the release
4. **Rollback Plan**: Procedure for rolling back if necessary

## Continuous Improvement

The release process is continuously improved through:

1. **Release Retrospectives**: Conducted after each release
2. **Metrics Collection**: Time to release, deployment success rate, etc.
3. **Feedback Loop**: Incorporating feedback from all stakeholders

## GitHub Actions Workflow

The release process is automated using GitHub Actions:

```yaml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
        
      - name: Build and push Docker images
        uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ghcr.io/username/eternia/backend:${{ github.ref_name }}
            ghcr.io/username/eternia/backend:latest
            
  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        uses: actions/deploy-to-kubernetes@v1
        with:
          namespace: eternia-production
          manifests: kubernetes/production/
```

## Release Checklist

### Pre-Release
- [ ] All features are complete and tested
- [ ] All tests are passing
- [ ] Documentation is updated
- [ ] Version numbers are updated
- [ ] Changelog is generated
- [ ] Release branch is created
- [ ] Staging deployment is successful
- [ ] UAT is completed

### Release
- [ ] Final approval is obtained
- [ ] Release tag is created
- [ ] Production deployment is triggered
- [ ] Deployment is verified
- [ ] Release branch is merged back to main

### Post-Release
- [ ] Application is monitored for issues
- [ ] User feedback is collected
- [ ] Release retrospective is scheduled
- [ ] Next release planning begins