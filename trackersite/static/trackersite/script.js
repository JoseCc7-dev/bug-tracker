document.addEventListener('DOMContentLoaded', () => {
    try {
        add = document.querySelector("#add_member")
        add.onclick = function() {add_member(document.querySelector("#team_members").value)}}
    catch{}

    try {
        changeProjectStatus = document.querySelector("#change_project_status") 
        changeProjectStatus.onclick = function() {finish_project(changeProjectStatus.value)}}
    catch{}
    console.log("test")
})
csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value
function add_member(user) {
    console.log(user)
    
    console.log(csrftoken)
    projectId = document.querySelector("#project_id").value
    
    fetch('/add-member', {
        method: 'POST', 
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            project_id: projectId,
            user: user,
          })
        })
        .then(response => {
            if (response.status == 400) {
                alert("Cannot add employee to project")
            }
            response.json()
        })
    location.reload()
}

function finish_project(newStatus) {
    projectId = document.querySelector("#project_id").value
    csrftoken = document.getElementsByName("csrfmiddlewaretoken")[0].value
    
    console.log(projectId)
    console.log(newStatus)
    fetch('/set-status', {
        method: 'POST', 
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            project_id: projectId,
            status: newStatus,
          })
        })
        .then(response => response.json())
    location.reload()
}

function role_select(id) {
    console.log("id:",id)
    var role = document.querySelector("#role_"+ id)
    var select = document.createElement("select")
    var option1 = document.createElement("option")
    var option2 = document.createElement("option")
    var option3 = document.createElement("option")
    var change = document.createElement("button")
    var user_role = document.querySelector("#user_role")


    option1.textContent = "Developer"
    option2.textContent = "Manager"
    option3.textContent = "Admin"
    
    if (option1.textContent === role.textContent) {
        console.log("check 1")
        option1.selected = true;
    }
    else if (option2.textContent === role.textContent) {
        console.log("check 2")
        option2.selected = true;
    }
    else {
        console.log("checks failed")
        option3.selected = true;
    }
    
    console.log("role:",user_role.textContent)
    change.textContent = "Change"
    change.className = "btn"
    change.addEventListener("click", () => {change_role(select.selectedOptions[0].value, id)})

    console.log(role.textContent)

    select.append(option1, option2, option3)
    role.textContent = ""
    role.append(select, change)

    console.log(role.textContent)
    return false
}

function change_role(value, id) {
    console.log("value:",value,"id:",id)

    fetch('/change-role', {
        method: 'PUT', 
        headers: {
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
            id: id,
            role: value,
          })
        })
        .then(response => response.json())
    location.reload()
}

function remove_user(id) {
    if (confirm("Are you sure you want to remove this user? This action cannot be undone.")) {
        console.log("removing")// fetch remove
        fetch('/remove-user', {
            method: 'PUT', 
            headers: {
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify({
                id: id,
              })
            })
            .then(response => response.json())
    }
    else {
        console.log("cancelled")
    }
    location.reload()
}