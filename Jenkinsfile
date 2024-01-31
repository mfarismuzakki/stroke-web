pipeline{
    environment {
        credentialId = 'aliregistry'
        url = "https://registry-intl.ap-southeast-5.aliyuncs.com"
        //scannerHome = tool 'Sonarqube'
        servicename = 'svc-data-dashboard'
        servicename2 = 'svc-data-dashboard-2'
    }

    agent { node { label 'agent1' } }
    //agent any 
    stages {
        stage('get envprod') {
            when { 
                branch 'main';
            }
            steps {
                withCredentials([file(credentialsId: 'env_data_dashboard_prod', variable: 'ini_env')]) {
                    sh "cat \$ini_env >> ${env.WORKSPACE}/.env"
                }
            } 
        }
        stage('Build Image main') {
            when { 
                branch 'main';
            }
            steps {
                slackSend (color: '#FFFF00', message: "STARTED: Build Image Main ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                echo 'Build Image main'
                sh 'docker build . -t ${servicename2}:${BRANCH_NAME}-${BUILD_NUMBER} --build-arg SSH_PRIVATE_KEY="$(cat ../id_rsa)"'
                sh 'echo ini build image main'
            }
        }
        stage('Docker Login tag push Main') {
            when { 
                branch 'main';
            }
            steps {
                script {
                    echo 'Push docker image ke docker registry Ali Main'
                    docker.withRegistry(url, credentialId) {
                        sh 'docker tag ${servicename2}:${BRANCH_NAME}-${BUILD_NUMBER} registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename2}:${BRANCH_NAME}-${BUILD_NUMBER}'
                        sh 'docker push registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename2}:${BRANCH_NAME}-${BUILD_NUMBER}'
                        sh 'echo ini docker login tag push Main'
                    }
                }
            }
        }
        stage('Set Image Kubernetes Main') {
            when { 
                branch 'main';
            }
            steps {
                script {
                    sh 'kubectl --kubeconfig="../../kubeconfig-dataeng-prod-premium.yaml" set image deployment ${servicename2} ${servicename2}=registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename2}:${BRANCH_NAME}-${BUILD_NUMBER} -n=dataeng'
                    sh 'echo set image k8s Main'
                }
            }
        }

        // //stage('Sonar Scanner With PR') {
        //     when {
        //         branch 'PR-*';
        //     }
        //     steps {
        //         script {
        //             withSonarQubeEnv('Sonarqube') {
        //                 def prKey = "-Dsonar.pullrequest.key=${env.CHANGE_ID}"
        //                 def prBranch = "-Dsonar.pullrequest.branch=${env.CHANGE_BRANCH}"
        //                 def prBase = "-Dsonar.pullrequest.base=${env.CHANGE_TARGET}"
        //                 // Run the scan
        //                 sh "${scannerHome}/bin/sonar-scanner ${prKey} ${prBranch} ${prBase}"
        //             }
        //             timeout(time: 10, unit: 'MINUTES') {
        //                 waitForQualityGate abortPipeline: true
        //             }
        //         }
        //     }
        //     post {
        //         success {
        //             slackSend (color: '#008000', message: "PASSED: Sonarqube PR ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //         failure {
        //             slackSend (color: '#FF0000', message: "FAILED: Sonarqube PR ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //     }   
        // }

        stage('Publish Approval') {
            when { 
                tag "release-*"
            }
            steps {
                script{
                //   input message: "Deploy these changes?", submitter "admin"
                def userName = input message: 'Deploy these changes?', submitter: "grandis,faris,admin", submitterParameter: "grandis,faris,admin"
                echo "Accepted by ${userName}"
                if (!(['grandis','faris','admin'].contains(userName))) {
                    error('This user is not approved to deploy to PROD.')
                }
                }
            }
        }

        // stage('Sonar Scanner Tag Release Prod') {
        //     when { 
        //         tag "release-*"
        //     }
        //     steps {
        //         script {
        //             withSonarQubeEnv('Sonarqube') {
        //                     sh "${scannerHome}/bin/sonar-scanner -Dsonar.branch.name=${env.BRANCH_NAME}"
        //             }
        //             timeout(time: 10, unit: 'MINUTES') {
        //                 waitForQualityGate abortPipeline: true
        //             }
        //         }
        //     }
        //     post {
        //         success {
        //             slackSend (color: '#008000', message: "PASSED: Sonarqube Prod ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //         failure {
        //             slackSend (color: '#FF0000', message: "FAILED: Sonarqube Prod ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //     }   
        // }
        stage('get env prod') {
            when { 
                tag "release-*"
            }
            steps {
                withCredentials([file(credentialsId: 'env_data_dashboard_prod', variable: 'ini_env_prod')]) {
                    sh "cat \$ini_env_prod >> ${env.WORKSPACE}/.env"
                }
            } 
        }
        stage('Build Image Tag Release Prod') {
            when { 
                tag "release-*"
            }
            steps {
                slackSend (color: '#FFFF00', message: "STARTED: Build Image Prod ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                echo 'Build Image Prod'
                sh 'docker build . -t ${servicename}:${BRANCH_NAME}-${BUILD_NUMBER} --build-arg SSH_PRIVATE_KEY="$(cat ../id_rsa)"'
                sh 'echo ini build image prod'
            }
            post {
                success {
                    slackSend (color: '#008000', message: "SUCCESS: Build Image Prod ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                }
                failure {
                    slackSend (color: '#FF0000', message: "FAILED: Build Image Prod ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                }
            }   
        }
        stage('Docker Login tag push Tag Release Prod') {
            when { 
                tag "release-*"
            }
            steps {
                script {
                    echo 'Push docker image ke docker registry Ali Prod'
                    docker.withRegistry(url, credentialId) {
                        sh 'docker tag ${servicename}:${TAG_NAME}-${BUILD_NUMBER} registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename}:${TAG_NAME}-${BUILD_NUMBER}'
                        sh 'docker push registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename}:${TAG_NAME}-${BUILD_NUMBER}'
                        sh 'echo ini docker login tag push prod'
                    }
                }
            }
        }
        stage('Set Image Kubernetes Tag Release Prod') {
            when { 
                tag "release-*"
            }
            steps {
                script {
                     sh 'kubectl --kubeconfig="../../kubeconfig-dataeng-prod-premium.yaml" set image deployment ${servicename} ${servicename}=registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename}:${TAG_NAME}-${BUILD_NUMBER} -n=dataeng'
                    sh 'echo set image k8s prod'
                }
            }
            post {
                success {
                    slackSend (color: '#008000', message: "SUCCESS: Deployment Prod ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                }
                failure {
                    slackSend (color: '#FF0000', message: "FAILED: Deployment Prod ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                }
            }
        }
        stage('Testing Automation Knowledge Center') {
           when { 
               tag "release-*"
           }
           steps {
               script {
                   sh 'pwd'
                   sh 'ls -l'
                   sh 'rm -rf doc-tools'
                   sh 'git clone https://bitbucket.org/klopos/doc-tools.git'
                   sh 'pwd'
                   sh 'ls -l'
                   sh 'cd doc-tools && pwd && ls -l && python3 main.py --name "SVC Data Dashboard" --token "mPIy2Jsl5iNUaG3JF6UDec1o8FGnRO7yGKI52J" --cid "575d0b8f-3803-42f1-8721-148d24d2f55a"'
               }
           }
        }

        // stage('Sonar Scanner Branch Master') {
        //     when { 
        //         branch 'master';
        //     }
        //     steps {
        //         script {
        //             withSonarQubeEnv('Sonarqube') {
        //                     sh "${scannerHome}/bin/sonar-scanner -Dsonar.branch.name=${env.BRANCH_NAME}"
        //             }
        //             timeout(time: 10, unit: 'MINUTES') {
        //                 waitForQualityGate abortPipeline: true
        //             }
        //         }
        //     }
        //     post {
        //         success {
        //             slackSend (color: '#008000', message: "PASSED: Sonarqube Branch Master ${env.BRANCH_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //         failure {
        //             slackSend (color: '#FF0000', message: "FAILED: Sonarqube Branch Master ${env.BRANCH_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //     }   
        // }
        
        // stage('Sonar Scanner Beta') {
        //     when { 
        //         branch 'staging';
        //     }
        //     steps {
        //         script {
        //                retry(5) {
        //                     withSonarQubeEnv('Sonarqube') {
        //                         sh "${scannerHome}/bin/sonar-scanner -Dsonar.branch.name=${env.BRANCH_NAME}"
        //                     }
        //                 }
        //                 timeout(time: 10, unit: 'MINUTES') {
        //                     waitForQualityGate abortPipeline: true
        //             }
        //         }
        //     }
        //     post {
        //         success {
        //             slackSend (color: '#008000', message: "PASSED: Sonarqube Beta ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //         failure {
        //             slackSend (color: '#FF0000', message: "FAILED: Sonarqube Beta ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //     }   
        // }
        // stage('Unit Test') {
        //     when { 
        //         branch 'staging_beta';
        //     }
        //     steps {
        //         script {
        //             nodejs(nodeJSInstallationName: 'nodejs') {
        //             sh 'npm -v'  //substitute with your code
        //             sh 'node -v'
        //             sh 'cd ./dev && npm install && npm test'
        //             } 
        //         }
        //     }
        // }
        stage('get env') {
            when { 
                branch 'staging';
            }
            steps {
                withCredentials([file(credentialsId: 'env_data_dashboard', variable: 'ini_env')]) {
                    sh "cat \$ini_env >> ${env.WORKSPACE}/.env"
                }
            } 
        }
        stage('Build Image Beta') {
            when { 
                branch 'staging';
            }
            steps {
                slackSend (color: '#FFFF00', message: "STARTED: Build Image Beta ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                echo 'Build Image beta'
                sh 'docker build . -t ${servicename}:${BRANCH_NAME}-${BUILD_NUMBER} --build-arg SSH_PRIVATE_KEY="$(cat ../id_rsa)"'
                sh 'echo ini build image beta'
            }
            post {
                success {
                    slackSend (color: '#008000', message: "SUCCESS: Build Image Beta ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                }
                failure {
                    slackSend (color: '#FF0000', message: "FAILED: Build Image Beta ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                }
            }   
        }
        stage('Docker Login tag push Beta') {
            when { 
                branch 'staging';
            }
            steps {
                script {
                    echo 'Push docker image ke docker registry Ali Beta'
                    docker.withRegistry(url, credentialId) {
                        sh 'docker tag ${servicename}:${BRANCH_NAME}-${BUILD_NUMBER} registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename}:${BRANCH_NAME}-${BUILD_NUMBER}'
                        sh 'docker push registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename}:${BRANCH_NAME}-${BUILD_NUMBER}'
                        sh 'echo ini docker login tag push Beta'
                    }
                }
            }
        }
        stage('Set Image Kubernetes Beta') {
            when { 
                branch 'staging';
            }
            steps {
                script {
                    sh 'kubectl --kubeconfig="../../kubeconfig-dataeng-stgpremium.yaml" set image deployment ${servicename} ${servicename}=registry-intl.ap-southeast-5.aliyuncs.com/majoo/${servicename}:${BRANCH_NAME}-${BUILD_NUMBER} -n=dataeng'
                    sh 'echo set image k8s Beta'
                }
            }
            post {
                success {
                    slackSend (color: '#008000', message: "SUCCESS: Deployment Beta ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                }
                failure {
                    slackSend (color: '#FF0000', message: "FAILED: Deployment Beta ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
                }
            }
        }
        //stage('Testing Automation Knowledge Center') {
        //    when { 
        //        branch 'staging';
        //    }
        //    steps {
        //        script {
        //            sh 'pwd'
        //            sh 'ls -l'
        //            sh 'rm -rf doc-tools'
        //            // git url: 'https://bitbucket.org/klopos/doc-tools.git'
        //            sh 'git clone https://bitbucket.org/klopos/doc-tools.git'
        //            sh 'pwd'
        //            sh 'ls -l'
        //            sh 'cd doc-tools && pwd && ls -l && python3 main.py --name "SVC Data Dashboard" --token "mPIy2Jsl5iNUaG3JF6UDec1o8FGnRO7yGKI52J" --cid "575d0b8f-3803-42f1-8721-148d24d2f55a"'
        //        }
        //    }
        //}
        
        // stage('Sonar Scanner Feature') {
        //     when { 
        //         branch 'feature/*';
        //     }
        //     steps {
        //         script {
        //             withSonarQubeEnv('Sonarqube') {
        //                     sh "${scannerHome}/bin/sonar-scanner -Dsonar.branch.name=${env.BRANCH_NAME}"
        //             }
        //             timeout(time: 10, unit: 'MINUTES') {
        //                 waitForQualityGate abortPipeline: true
        //             }
        //         }
        //     }
        //     post {
        //         success {
        //             slackSend (color: '#008000', message: "PASSED: Sonarqube Feature ${env.BRANCH_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //         failure {
        //             slackSend (color: '#FF0000', message: "FAILED: Sonarqube Feature ${env.BRANCH_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //     }   
        // }
        // stage('Sonar Scanner Hotfix') {
        //     when { 
        //         branch 'hotfix/*';
        //     }
        //     steps {
        //         script {
        //             withSonarQubeEnv('Sonarqube') {
        //                     sh "${scannerHome}/bin/sonar-scanner -Dsonar.branch.name=${env.BRANCH_NAME}"
        //             }
        //             timeout(time: 10, unit: 'MINUTES') {
        //                 waitForQualityGate abortPipeline: true
        //             }
        //         }
        //     }
        //     post {
        //         success {
        //             slackSend (color: '#008000', message: "PASSED: Sonarqube Hotfix ${env.BRANCH_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //         failure {
        //             slackSend (color: '#FF0000', message: "FAILED: Sonarqube Hotfix ${env.BRANCH_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        //         }
        //     }   
        // }
    }
    post {
        success {
            slackSend (color: '#008000', message: "SUCCESS: Pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        }
        failure {
            slackSend (color: '#FF0000', message: "FAILED: Pipeline ${env.JOB_NAME} #${env.BUILD_NUMBER} (<${env.BUILD_URL}|Open>)")
        }
    }
}