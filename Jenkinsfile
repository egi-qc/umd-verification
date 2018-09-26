pipeline {
  agent {
      label 'python'
  }
  stages {
    stage('Test') {
      steps {
        sh 'tox -e pep8'
      }
    }
  }
}
