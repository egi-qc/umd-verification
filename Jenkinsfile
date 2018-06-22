pipeline {
  agent {
    //node {
      //label 'python'
      //docker.withServer('tcp://172.16.39.13:2375', '') {
      
      //docker { image 'indigodatacloud/ci-images:python' }
      
      docker.image('indigodatacloud/ci-images:python') {
        sh 'tox -e pep8'
      }
      //}
    //}
  }
  stages {
    stage('Test') {
      steps {
        sh 'tox -e pep8'
      }
    }
  }
}
