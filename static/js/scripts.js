
// Replace with your own API keys and credentials
const GOOGLE_API_KEY = 'AIz';
const GOOGLE_CLIENT_ID = '8879ent.com';
const MICROSOFT_APP_ID = 'cdfc16';
const MICROSOFT_APP_SECRET = 'a2dT';

// Google Calendar integration
function handleClientLoad() {
    gapi.load('client:auth2', initClient);
}

function initClient() {
    gapi.client.init({
        apiKey: GOOGLE_API_KEY,
        clientId: GOOGLE_CLIENT_ID,
        discoveryDocs: ["https://www.googleapis.com/discovery/v1/apis/calendar/v3/rest"],
        scope: "https://www.googleapis.com/auth/calendar.readonly"
    }).then(() => {
        gapi.auth2.getAuthInstance().isSignedIn.listen(updateSigninStatus);
        updateSigninStatus(gapi.auth2.getAuthInstance().isSignedIn.get());
    }, (error) => {
        console.log(JSON.stringify(error, null, 2));
    });
}

function updateSigninStatus(isSignedIn) {
    const authorizeButton = document.getElementById('authorize_button');
    const signoutButton = document.getElementById('signout_button');
    const calendarContent = document.getElementById('calendar_content');

    if (calendarContent) {
        if (isSignedIn) {
            authorizeButton.style.display = 'none';
            signoutButton.style.display = 'block';
            calendarContent.style.display = 'block';
            listUpcomingEvents();
        } else {
            authorizeButton.style.display = 'block';
            signoutButton.style.display = 'none';
            calendarContent.style.display = 'none';
        }

        authorizeButton.onclick = handleAuthClick;
        signoutButton.onclick = handleSignoutClick;
    }
}

function handleAuthClick() {
    gapi.auth2.getAuthInstance().signIn();
}

function handleSignoutClick() {
    gapi.auth2.getAuthInstance().signOut();
}

function listUpcomingEvents() {
    gapi.client.calendar.events.list({
        'calendarId': 'primary',
        'timeMin': (new Date()).toISOString(),
        'showDeleted': false,
        'singleEvents': true,
        'maxResults': 10,
        'orderBy': 'startTime'
    }).then((response) => {
        const events = response.result.items;
        const calendarContent = document.getElementById('calendar_content');

        if (events.length > 0) {
            calendarContent.innerHTML = '<ul>';
            for (let i = 0; i < events.length; i++) {
                const event = events[i];
                const start = event.start.dateTime || event.start.date;
                calendarContent.innerHTML += `<li>${start} - ${event.summary}</li>`;
            }
            calendarContent.innerHTML += '</ul>';
        } else {
            calendarContent.innerHTML = 'No upcoming events found.';
        }
    });
}

// OneNote integration
function authorizeOneNote() {
    const msftAuthUrl = `https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=${MICROSOFT_APP_ID}&response_type=code&redirect_uri=${encodeURIComponent('<YOUR_REDIRECT_URI>')}&response_mode=query&scope=offline_access%20User.Read%20Notes.ReadWrite.All&state=<YOUR_STATE_VALUE>`;
    window.location.href = msftAuthUrl;
}

//document.getElementById('onenote_button').addEventListener('click', authorizeOneNote);
const oneNoteButton = document.getElementById('onenote_button');
if (oneNoteButton) {
    oneNoteButton.addEventListener('click', authorizeOneNote);
}


// Load the Google Calendar API client
document.addEventListener('DOMContentLoaded', handleClientLoad);
