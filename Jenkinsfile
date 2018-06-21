pipeline {
  agent {
    node {
      docker.withServer('tcp://172.16.39.13:2375', '') {
      }
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
