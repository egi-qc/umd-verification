pipeline {
  agent {
    node {
      //label 'python'
      //docker.withServer('tcp://172.16.39.13:2375', '') {
      //docker.image('indigodatacloud/ci-images:python') {
      //  sh 'tox -e pep8'
      //}
      docker { image 'indigodatacloud/ci-images:python' }
      //}
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
