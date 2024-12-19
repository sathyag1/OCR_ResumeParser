node {
    def app
    workspace = env.WORKSPACE

    stage('Clone repository') {
        /* Let's make sure we have the repository cloned to our workspace */

        checkout scm
    }

    stage('Build image') {
        /* This builds the actual image; synonymous to
         * docker build on the command line */

        app = docker.build("resumeparser:latest", "${env.WORKSPACE}/")
    }

    stage('Push image') {
        /* Finally, we'll push the image with two tags:
         * First, the incremental build number from Jenkins
         * Second, the 'latest' tag.
         * Pushing multiple tags is cheap, as all the layers are reused. */
        docker.withRegistry('https://yuwspkuatappacr1.azurecr.io', '5393f678-b0fe-41e1-bc89-0307f74fe367') {
            app.push("${env.BUILD_NUMBER}")
            app.push("latest")
        }
    }
}
