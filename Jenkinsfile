// Jenkinsfile - qiyuan_project (Declarative Pipeline)
// 使用方式：Jenkins 任务类型选 "Pipeline", "Pipeline script from SCM" 指向本仓库,
//          "Script Path" 填 Jenkinsfile。
// 旧自由风格任务（直接调用 jenkins_build_robust.bat）也可保留并继续使用本脚本。

pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 60, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    environment {
        ALLURE_RESULTS_DIR = 'allure-results'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build & Test') {
            steps {
                bat 'call jenkins_build_robust.bat'
            }
        }

        stage('Generate Allure Report') {
            steps {
                allure includeProperties: false,
                      jdk: '',
                      results: [[path: env.ALLURE_RESULTS_DIR]]
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'allure-report/**/*,allure-results/**/*',
                             allowEmptyArchive: true,
                             fingerprint: false
        }
        failure {
            echo '构建失败，请查看上方日志定位问题。'
        }
        success {
            echo '构建成功。'
        }
    }
}
