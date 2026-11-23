pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out CourseCompass repository...'
            }
        }
        stage('Install & Lint') {
            steps {
                sh 'pip install -r backend/requirements.txt pylint bandit'
                sh 'pylint backend/app --exit-zero'
            }
        }
        stage('Test & Coverage') {
            steps {
                sh 'pytest tests/test_coursecompass.py --cov=backend/app --cov-fail-under=80'
            }
        }
        stage('Package Docker Image') {
            steps {
                sh 'docker build -t coursecompass-api:v1.0 ./backend'
            }
        }
    }
}
