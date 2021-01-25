#!/usr/bin/env groovy

library("govuk")

REPOSITORY = 'mapit'

node {

  try {
    stage('Checkout') {
      govuk.checkoutFromGitHubWithSSH(REPOSITORY)
      govuk.cleanupGit()
      govuk.mergeMasterBranch()
    }

    stage('Installing Packages') {
      sh("rm -rf venv")
      sh("python3.6 -m venv venv")
      sh("venv/bin/python -m pip install --upgrade pip wheel setuptools")
      sh("venv/bin/python -m pip install -r requirements.txt")
    }

    stage('Tests') {
      govuk.setEnvar("GOVUK_ENV", "ci")
      sh("venv/bin/python manage.py test --noinput mapit mapit_gb")
    }

    if (env.BRANCH_NAME == 'master') {
      stage('Push release tag') {
        govuk.pushTag(REPOSITORY, BRANCH_NAME, 'release_' + BUILD_NUMBER)
      }

      stage('Deploy to Integration') {
        govuk.deployIntegration(REPOSITORY, BRANCH_NAME, 'release_' + BUILD_NUMBER, 'deploy')
      }
    }
  } catch (e) {
    currentBuild.result = 'FAILED'
    step([$class: 'Mailer',
          notifyEveryUnstableBuild: true,
          recipients: 'govuk-ci-notifications@digital.cabinet-office.gov.uk',
          sendToIndividuals: true])
    throw e
  }

  // Wipe the workspace
  deleteDir()
}
