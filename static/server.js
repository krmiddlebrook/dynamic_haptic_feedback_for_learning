const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const bodyParser = require('body-parser');

const app = express()
const port = 3000

var preQuizCount = 0
var postQuizCount = 0

var pastTime = (new Date).getTime();

app.use(bodyParser.urlencoded({extended: true}));
app.use(bodyParser.json());

app.use('/static', express.static(__dirname + '/'));

let db = new sqlite3.Database('user-info.db', (err) => {
  if (err) {
    return console.error(err.message);
  }
  console.log('Connected to the in-memory SQlite database.');
});

app.get('/', function(req, res) {
	res.sendFile(__dirname + '/initialpage.html');
});

app.get('/likert', function(req, res) {
	res.sendFile(__dirname + '/likerthome.html');
})

app.post('/submit', function(req, res) {
	addPerson(req.body.firstName, req.body.lastName);
	res.sendFile(__dirname + '/q1.html');
	pastTime = (new Date).getTime();
});

app.post('/q1submit', function(req, res) {
	addQuestion1Answer(req.body.q1answer);
	res.sendFile(__dirname + '/q2.html');
	var newTime = (new Date).getTime();
	var timeQ1Took = newTime - pastTime;
	pastTime = newTime;
	db.run(`UPDATE Persons SET q1time = '${timeQ1Took}' WHERE PersonID = ${preQuizCount};`);
	// console.log(timeQ1Took);
});

app.post('/q2submit', function(req, res) {
	addQuestion2Answer(req.body.q2answer);
	res.sendFile(__dirname + '/q3.html');
	var newTime = (new Date).getTime();
	var timeQ2Took = newTime - pastTime;
	pastTime = newTime;
	db.run(`UPDATE Persons SET q2time = '${timeQ2Took}' WHERE PersonID = ${preQuizCount};`);
	// console.log(timeQ2Took);
});

app.post('/q3submit', function(req, res) {
	addQuestion3Answer(req.body.q3answer);
	res.sendFile(__dirname + '/q4.html');
	var newTime = (new Date).getTime();
	var timeQ3Took = newTime - pastTime;
	pastTime = newTime;
	db.run(`UPDATE Persons SET q3time = '${timeQ3Took}' WHERE PersonID = ${preQuizCount};`);
	// console.log(timeQ3Took);
});

app.post('/q4submit', function(req, res) {
	addQuestion4Answer(req.body.q4answer);
	res.sendFile(__dirname + '/done.html');
	var newTime = (new Date).getTime();
	var timeQ4Took = newTime - pastTime;
	pastTime = newTime;
	db.run(`UPDATE Persons SET q4time = '${timeQ4Took}' WHERE PersonID = ${preQuizCount};`);
	// console.log(timeQ4Took);
});

app.post('/likertnamesubmit', function(req, res) {
	db.run(`INSERT INTO LikertResults (ID, FirstName, LastName) VALUES ('${++postQuizCount}', '${req.body.firstName}', '${req.body.lastName}');`);
	res.sendFile(__dirname + '/likert.html');
});

app.post('/likertsubmit', function(req, res) {
	db.run(`UPDATE LikertResults SET q1 = '${req.body.q1}' WHERE ID = ${postQuizCount};`);
	db.run(`UPDATE LikertResults SET q2 = '${req.body.q2}' WHERE ID = ${postQuizCount};`);
	db.run(`UPDATE LikertResults SET q3 = '${req.body.q3}' WHERE ID = ${postQuizCount};`);
	db.run(`UPDATE LikertResults SET q4 = '${req.body.q4}' WHERE ID = ${postQuizCount};`);
	res.sendFile(__dirname + '/done.html');
});

app.listen(port, () => console.log(`App listening on port ${port}!`))

function addPerson(firstName, lastName) {
	db.run(`INSERT INTO Persons (PersonID, LastName, FirstName) VALUES ('${++preQuizCount}', '${lastName}', '${firstName}');`);
}

function addQuestion1Answer(answer) {
	db.run(`UPDATE Persons SET q1 = '${answer}' WHERE PersonID = ${preQuizCount};`);
}

function addQuestion2Answer(answer) {
	db.run(`UPDATE Persons SET q2 = '${answer}' WHERE PersonID = ${preQuizCount};`);
}

function addQuestion3Answer(answer) {
	db.run(`UPDATE Persons SET q3 = '${answer}' WHERE PersonID = ${preQuizCount};`);
}

function addQuestion4Answer(answer) {
	db.run(`UPDATE Persons SET q4 = '${answer}' WHERE PersonID = ${preQuizCount};`);
}

// db.close((err) => {
//   if (err) {
//     return console.error(err.message);
//   }
//   console.log('Close the database connection.');
// });