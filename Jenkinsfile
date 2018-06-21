pipeline {
  agent any
  stages {
    stage('Test') {
      steps {
        sh 'tox -e pep8'
      }
    }
  }
}