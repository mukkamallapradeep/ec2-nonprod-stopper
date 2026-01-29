pipeline {
  agent any

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build & Deploy') {
      steps {
        sh '''
          docker-compose --version
          docker-compose down || true
          docker-compose build --no-cache
          docker-compose up -d
          docker-compose ps

        '''
      }
    }
  }
}
