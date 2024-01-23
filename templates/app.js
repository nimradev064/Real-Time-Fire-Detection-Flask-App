const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');

const app = express();

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017', { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log('Connected to MongoDB'))
    .catch(err => console.error('Error connecting to MongoDB', err));

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.set('view engine', 'ejs');

// Define a MongoDB schema and model
const CameraSchema = new mongoose.Schema({
    uniqueId: Number,
    ipAddress: String,
});

const CameraModel = mongoose.model('Camera', CameraSchema);

// Serve your HTML file
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/Add_camera.html');
});

// Handle form submission and save data
app.post('/register-camera', (req, res) => {
    const { uniqueId, ipAddress } = req.body;

    // Create a new Camera instance
    const camera = new CameraModel({
        uniqueId,
        ipAddress,
    });

    // Save the camera data to MongoDB
    camera.save()
        .then(() => {
            console.log('Camera data saved to MongoDB');
            res.redirect('/');
        })
        .catch(err => {
            console.error('Error saving camera data to MongoDB', err);
            res.redirect('/');
        });
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
