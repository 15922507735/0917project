// Jenkinsfile - qiyuan_project (Declarative Pipeline)
// 框架：Appium-Python-client 6.x + Pytest + PO 分层
//       (page_element / object_operation / testcase_manage)
// 测试入口：python cli.py [smoke|regression]（由 jenkins_build_robust.bat 调用）
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
        // 邮件通知：成功、失败、不稳定、aborted 都发送
        // 依赖：Email-ext Plugin；Jenkins 系统配置里要配 SMTP + Admin Email
        // 收件人：594608047@qq.com
        success {
            mail to: '594608047@qq.com',
                 subject: "✓ ${env.JOB_NAME} #${env.BUILD_NUMBER} 构建成功",
                 body: """<p>构建 <b>${env.JOB_NAME} #${env.BUILD_NUMBER}</b> 已通过。</p>
                 <ul>
                   <li>状态: SUCCESS</li>
                   <li>时长: ${currentBuild.durationString}</li>
                   <li>Allure 报告: <a href="${env.BUILD_URL}allure">${env.BUILD_URL}allure</a></li>
                   <li>控制台: <a href="${env.BUILD_URL}console">${env.BUILD_URL}console</a></li>
                 </ul>
                 <p>查看 Allure 报告中的用例通过/失败统计。</p>"""
        }
        failure {
            mail to: '594608047@qq.com',
                 subject: "✗ ${env.JOB_NAME} #${env.BUILD_NUMBER} 构建失败",
                 body: """<p>构建 <b>${env.JOB_NAME} #${env.BUILD_NUMBER}</b> 失败，请尽快排查。</p>
                 <ul>
                   <li>状态: FAILURE</li>
                   <li>时长: ${currentBuild.durationString}</li>
                   <li>Allure 报告: <a href="${env.BUILD_URL}allure">${env.BUILD_URL}allure</a></li>
                   <li>控制台: <a href="${env.BUILD_URL}console">${env.BUILD_URL}console</a></li>
                 </ul>
                 <p>点击 Allure 链接查看失败用例 traceback。</p>"""
        }
        unstable {
            mail to: '594608047@qq.com',
                 subject: "⚠ ${env.JOB_NAME} #${env.BUILD_NUMBER} 构建不稳定",
                 body: """<p>构建 <b>${env.JOB_NAME} #${env.BUILD_NUMBER}</b> 不稳定（有失败用例）。</p>
                 <ul>
                   <li>状态: UNSTABLE</li>
                   <li>Allure 报告: <a href="${env.BUILD_URL}allure">${env.BUILD_URL}allure</a></li>
                 </ul>"""
        }
    }
}

