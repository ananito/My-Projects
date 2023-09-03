document.addEventListener('DOMContentLoaded', function () {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector("#compose-form").onsubmit = send_mail;


  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(reply) {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#mailbox-view').style.display = 'none';

  // Clear out composition fields
  if (reply) {
    document.querySelector('#compose-recipients').value = '';
    document.querySelector('#compose-subject').value = '';
    document.querySelector('#compose-body').value = '';
  }

}

function load_mailbox(mailbox) {

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  if (mailbox === "inbox") {
    return list_inbox();

  } else if (mailbox === "sent") {
    return list_inbox("sent");
  } else if (mailbox === "archive") {
    return list_inbox("archive");
  }
}

function message(message, type) {
  if (document.querySelector(".message")) {
    document.querySelector(".message").className = `alert message alert-${type} alert-dismissible fade show`
    document.querySelector(".message-text").innerHTML = message;
  } else {
    const alert = `<div class="alert message alert-${type} alert-dismissible fade show" role="alert">
                      <p class="message-text">${message}</p>
                      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;
    document.querySelector("#message").innerHTML = alert;
  }

}

function validate_email(email) {
  let re = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;

  return re.test(email);
}

function send_mail() {
  let mail_sender = document.querySelector("#compose-sender");
  let mail_recipients = document.querySelector("#compose-recipients");
  let mail_subject = document.querySelector("#compose-subject");
  let mail_body = document.querySelector("#compose-body");
  if (mail_recipients.value == "") {
    message("Please Insert one or more recipient(s) email.", "danger");
    return false;

  }

  let emails = mail_recipients.value.split(",");
  if (emails.length > 1) {


    for (const email of emails) {
      if (!validate_email(email.trim())) {
        message(`This email: ${email} is invalid`, "danger");
        // console.log(email);
        return false;

      }
    }
  } else if (emails.length == 1) {

    if (!validate_email(emails)) {
      // console.log(emails);
      message("Hello", "danger")
      return false;

    }
  }

  if (mail_body.value == "") {
    message("Please some content in the body!", "danger");
    return false;
  }

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: emails.toString(),
      subject: mail_subject.value,
      body: mail_body.value
    })
  })
    .then(response =>
      response.json())
    .then(result => {
      // Print result
      if (result.error) {
        message(result.error, "danger");
      } else {
        message(result.message, "primary")

      }
    });

  load_mailbox('sent');
  return false;
}

function list_inbox(type = "inbox") {


  document.querySelector('#mailbox-view').style.display = 'block';

  document.querySelector('#inbox-items').innerHTML = '';


  fetch(`/emails/${type}`)
    .then(response => response.json())
    .then(emails => {
      // Print emails
      // console.log(emails);
      

      emails.forEach(email => {

      // check to see if there is a subject
      if (email.subject === "") {
        email.subject = "(no subject)";
      }

        let html = `
                      <div class="col">
                        <div class="row">
                            <div class="col-md-2">
                                <span class="fw-bolder bold" id="sender">${email.sender}</span>
                            </div>
                            <div class="col-md-8">
                                <p class="text-truncate">
                                    <span class="fw-bolder bold" id="subject">${email.subject}</span> -  ${email.body}</p>
                            </div>
                            <div class="col-md-2 text-end">
                                <p class="fw-bolder bold" id="date">${email.timestamp}</p>
                            </div>
                        </div>
                    </div>
                `;


        let list_container = document.createElement("li");
        list_container.className = "list-group-item inbox-item";
        list_container.dataset.emailId = email.id;
        list_container.innerHTML = html;
        document.querySelector("#inbox-items").appendChild(list_container);

        // check to see if the email is read
        if (email.read === true) {
          // make the back ground grey
          list_container.classList.add("list-group-item-secondary");

          // loop over all element that has bold as a class and remove fw-bolder
          list_container.querySelectorAll(".bold").forEach(bold => {
            bold.classList.remove("fw-bolder")
          });
        }


        // console.log(email);
      });

      // Get all emails from the inbox
      let inbox_items = document.querySelectorAll(".inbox-item");


      // iterate through all inbox_items
      for (const item of inbox_items) {

        // add a click listener
        item.addEventListener("click", function () {

          // when click is pressed change the color to grey
          item.classList.add("list-group-item-secondary");



          // change all bold texts in the email into read text
          item.querySelectorAll(".bold").forEach(bold => {
            // remove the class name that makes the element bold
            bold.classList.remove("fw-bolder");

            // check to see if the email is sent from the user
            if (type === "sent") {
              return view_email(item.dataset.emailId, true);

            }
            return view_email(item.dataset.emailId);
          });
        });
      }

    });
}

function email_read(id) {
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      read: true
    })
  })
}

function archive(id, yes = true) {
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: yes
    })
  })
}

function view_email(id, sent) {

  // hide mailbox view
  document.querySelector('#mailbox-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'none';



  fetch(`/emails/${id}`)
    .then(response => response.json())
    .then(email => {

      // set email to read
      email_read(id);

      if (email.subject === "") {
        email.subject = "(no subject)";
      }
      let html = `<div class="col-md">
                      <div class="col text-start">
                          <h4><strong>${email.subject}</strong></h4>
                      </div>
                  </div>
                  <hr>
                  <div class="row">
                      <div class="col-md">
                          <strong>${email.sender}</strong>
                      </div>
                      <div class="col-md text-end">
                          <div class="row">
                          <div class="col-sm">
                              <p class="fw-bolder d-inline">${email.timestamp.toString()}</p>
                              <button class="btn btn-sm btn-outline-primary" id="btn-archive" type="submit">Archived</button>
                              <button class="btn btn-sm btn-outline-primary" id="btn-reply" type="submit">Reply</button>

                          </div>
                          </div>
                      </div>
                  </div>
                  <div class="col-md mt-5">
                      <p class="lh-base">${email.body.replaceAll("\n", "<br>")}</p>
                  </div>
                  <hr/>`;

      let content = document.querySelector("#emails-view");
      content.style.display = 'block';
      content.innerHTML = html;


      // check if the email is archived
      let btn_archive = content.querySelector("#btn-archive");
      if (email.archived === false) {
        btn_archive.addEventListener("click", function () {
          archive(id, true);
          btn_archive.className = "btn btn-sm btn-outline-danger";

          btn_archive.innerHTML = "Unarchive";
          setTimeout(() => {
            load_mailbox("archive");
          }, 200);

        });

      } else if (email.archived === true) {
        btn_archive.className = "btn btn-sm btn-outline-danger";
        btn_archive.innerHTML = "Unarchive";
        btn_archive.addEventListener("click", function () {

          // set the email to unarchived
          archive(id, false);

          // remove the red outline
          btn_archive.classList.remove("btn-outline-danger");

          // add the blue outline
          btn_archive.classList.add("btn-outline-primary");

          // change the innerhtml to archive from unarchive
          btn_archive.innerHTML = "Archive";

          // wait for about 200mx before load loading the inbox
          setTimeout(() => {
            load_mailbox("inbox");
          }, 200);
        });
      }


      // chech if the user sent this email
      if (sent === true) {
        console.log("dfhdsa");
        btn_archive.remove();        
      }
      


      // check to see if reply btn is pressed
      content.querySelector("#btn-reply").addEventListener("click", () => {
        console.log("Hello, World");


        // set the values of the reply email
        document.querySelector("#compose-recipients").value = email.sender;

        // check to see if there is Re: infront the subject
    
        let subject = /^(re:\s|Re:\s)/
        if (subject.test(email.subject)) {
          document.querySelector('#compose-subject').value = email.subject;
        } else {
          document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
        }
        document.querySelector('#compose-body').value = `\n\non ${email.timestamp.toString()} ${email.sender} wrote: \n ${email.body}`;
        compose_email(false);

      });



    });

return false;
}
