document.addEventListener("DOMContentLoaded", () => {

    // For Follow Button
    follow();


    // This is for the edit button
    edit();

    // This is for Like Button
    like();
    
});


function follow() {
      // This is for the follow and unfollow button
      try {
        let follow = document.querySelector("#follow");
        follow.addEventListener("click", function () {
            fetch("/follow", {
                method: "POST",
                body: JSON.stringify({
                    user: follow.dataset.follow
                })
            })
            .then(response => {
                if (response.ok) {

                    return response.json();
                }
                return Promise.reject(response);
            })
            .then(anwser => {
    
                let followerbtn = document.querySelector("#followers");
    
    
                if (follow.innerHTML === "Follow") {
                    follow.classList.remove("btn-primary");
                    follow.classList.add("btn-danger")
                    follow.innerHTML = "Unfollow";
                    followerbtn.innerHTML = Number(followerbtn.innerHTML) + 1;
    
                }
                else if (follow.innerHTML === "Unfollow") {
                    follow.classList.remove("btn-danger");
                    follow.classList.add("btn-primary")
                    follow.innerHTML = "Follow";
                    followerbtn.innerHTML = Number(followerbtn.innerHTML) - 1;
                }
            })
            .catch(response => {
               return;
            });
        });
    }
    catch {
        return ;
    }
}

function edit() {
        document.querySelectorAll("#posts").forEach(post => {
            try {

            
                let editbtn = post.querySelector("#editbtn");
                
                editbtn.addEventListener("click", () => {
                    if (editbtn.innerHTML === "Edit") {
                        let postbody = post.querySelector("#post-body").innerHTML;
                        let p = post.querySelector("#post-body");
                        let textarea = document.createElement("textarea");
                        textarea.classList = "form-control";
                        textarea.id = "post-body";
                        textarea.rows = 4;
                        textarea.innerHTML = postbody.trim();
                        p.replaceWith(textarea);
                        editbtn.innerHTML = "Save";
                    } else if (editbtn.innerHTML === "Save") {
                        let postbody = post.querySelector("#post-body").value;
                        let textarea = post.querySelector("#post-body");
                        let p = document.createElement("p");
                        p.id = "post-body";
                        p.innerHTML = postbody.trim();
                        textarea.replaceWith(p);
                        postUpdate(editbtn.dataset.id, postbody.trim());
                        editbtn.innerHTML = "Edit";
                    }
                });
            }catch{
                return;
            }
        });
    
}

function postUpdate(postId, postBody) {
    try {
        fetch("/postupdate", {
            method: "PUT",
            body: JSON.stringify({
                postId: postId,
                postBody: postBody
            })
        })
        .then (response => response.json())
        .then(message => {
            let msg = `<div class="alert alert-success alert-dismissible fade show" role="alert">
                Post Saved Successfully!
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
          </div>`;
          let newelemet = document.createElement("div");
            newelemet.innerHTML = msg;
          document.querySelector(".body").prepend(newelemet);
        });
    } catch (error) {
        return;
    }
}

function like() {
    document.querySelectorAll("#posts").forEach(post => {
        try {
            let likebtn = post.querySelector("#like");

            likebtn.addEventListener("click", () => {
                let icon = likebtn.querySelector("#icon");
                let likecount = likebtn.querySelector("#likecount");
    
    
                fetch("/like", {
                    method: "PUT",
                    body: JSON.stringify({postId: Number(likebtn.dataset.id)})
                })
                .then(response => {
    
    
                    if (response.ok) {
                        return response.json();
                    }
                    return Promise.reject(response);
                
                })
                .then(answer => {
    
                    if (icon.classList.contains("fa-regular")) {
                        icon.classList.remove("fa-regular");
                        icon.classList.add("fa-solid");
                    } else if (icon.classList.contains("fa-solid")) {
                        icon.classList.remove("fa-solid");
                        icon.classList.add("fa-regular")
                    }
    
                    likecount.innerHTML = answer.likes;
    
                })
                .catch(response => {
                    console.log(response);
                });
            });


        } catch (error) {
            return;
        }
      
    });
}