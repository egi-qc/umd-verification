pipeline {
  agent {
    node {
    }
    
  }
  stages {
    stage('Test') {
      steps {
        sh 'tox -e pep8'
      }
    }
  }
}
