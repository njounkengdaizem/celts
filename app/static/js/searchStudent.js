import searchUser from './searchUser.js'
function callback(selected) {
  $("#searchStudent").submit();
}

$("#searchStudentsInput").on("input", function() {
  searchUser("searchStudentsInput", callback);
});
