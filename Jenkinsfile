pipeline {
  agent any
  stages {
    stage('Test') {
      agent {
        docker {
          image 'indigodatacloud/ci-images:python'
        }
        
      }
      steps {
        sh 'tox -e pep8'
      }
    }
  }
}