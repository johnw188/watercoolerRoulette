<script>
    let user = { loggedIn: false }
</script>

<main>
    {#if user.loggedIn}
    <button>Do the thing!</button>
    {:else}
    <a href="https://slack.com/oauth/authorize?scope=users.profile:read,users:read,users:read.email,identify&client_id=241546863697.1005448378753&redirect_uri=https%3A%2F%2Fapi.watercooler.express%2Fauth"><img alt="Sign in with Slack" height="40" width="172" src="https://platform.slack-edge.com/img/sign_in_with_slack.png" srcset="https://platform.slack-edge.com/img/sign_in_with_slack.png 1x, https://platform.slack-edge.com/img/sign_in_with_slack@2x.png 2x" /></a>
    {/if}
</main>
