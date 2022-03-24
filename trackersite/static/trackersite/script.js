document.addEventListener('DOMContentLoaded', () => {
    add = document.querySelector("#add_member")
    add.onclick = function() {add_member(document.querySelector("#team_members").value)}

})

function add_member(user) {
    console.log(user)
    csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value
    console.log(csrftoken)
    projectId = document.querySelector("#project_id").value
    role = document.querySelector("#member_role").value
    
    fetch('/add-member', {
        method: 'POST', 
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            project_id: projectId,
            user: user,
            role: role,
          })
        })
        .then(response => response.json())
    location.reload()
}

fetch('/send' , {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify({
        user: message,
        project: room,
        user: user
    })
  })
  .then(response => response.json())