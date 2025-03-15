/* App.js */
import React, { useState } from "react";
import axios from "axios";
import "./styles.css";

function App() {
  const [image, setImage] = useState(null);
  const [imagePath, setImagePath] = useState("");
  const [caption, setCaption] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [captionAudioUrl, setCaptionAudioUrl] = useState(""); // Audio for caption
  const [qaAudioUrl, setQaAudioUrl] = useState(""); // Audio for Q&A
  const [loadingCaption, setLoadingCaption] = useState(false);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [dragging, setDragging] = useState(false);

  const handleImageUpload = async (file) => {
    if (!file) return;

    setLoadingCaption(true);
    setCaption("");
    setImage(URL.createObjectURL(file));

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await axios.post("http://localhost:5000/upload", formData);
      setCaption(response.data.caption);
      setImagePath(response.data.image_path);

      // Ensure FULL URL for Audio
      if (response.data.caption_audio_url) {
        // setCaptionAudioUrl(response.data.caption_audio_url);
        const absoluteUrl = `http://localhost:5000${response.data.caption_audio_url}`;
        console.log("Audio URL:", absoluteUrl);
        setCaptionAudioUrl(absoluteUrl);
      }
    } catch (error) {
      console.error("Error uploading image:", error);
    } finally {
      setLoadingCaption(false);
    }
  };

  const onFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      handleImageUpload(file);
    }
  };

  const onDragOver = (event) => {
    event.preventDefault();
    setDragging(true);
  };

  const onDragLeave = () => {
    setDragging(false);
  };

  const onDrop = (event) => {
    event.preventDefault();
    setDragging(false);
    const file = event.dataTransfer.files[0];
    if (file) {
      handleImageUpload(file);
    }
  };

  const handleAskQuestion = async () => {
    if (!question) return;

    setLoadingAnswer(true);  //  Step 1: Show "Processing answer..."
    setAnswer("");           //  Step 2: Clear previous answer
    setQaAudioUrl("");       // Step 3: Clear previous audio

    setTimeout(() => { }, 0); //  Step 4: Force UI update immediately

    try {
      const response = await axios.post("http://localhost:5000/ask", {
        image_path: imagePath,
        question: question
      });

      setAnswer(response.data.answer);

      if (response.data.qa_audio_url) {
        const absoluteUrl = `http://localhost:5000${response.data.qa_audio_url}`;
        console.log("Audio URL:", absoluteUrl);
        setQaAudioUrl(absoluteUrl);
      }
    } catch (error) {
      console.error("Error fetching answer:", error);
    } finally {
      setLoadingAnswer(false); // Hide "Processing..." when API returns
    }
  };





  return (
    <div>
      {/* Header Section */}
      <div className="header">
        <h1>AI Wizards - Image Captioning & Q&A</h1>
        <p className="branding">Empowering AI-driven Visual Understanding</p>
      </div>

      {/* Content Section */}
      <div className="content-container">
        {/* Upload, Image, and Caption Section (Left) */}
        <div className="upload-caption-container">
          <div
            className={`upload-section ${dragging ? "dragging" : ""}`}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
          >
            <h2>Upload Your Image Here</h2>
            <p>Drag & drop an image, or click below to choose a file</p>

            {!image ? (
              <input type="file" onChange={onFileChange} />
            ) : (
              <button
                className="choose-file-btn"
                onClick={() => {
                  setImage(null);
                  setImagePath("");
                  setCaption("");
                  setCaptionAudioUrl("");
                  setQuestion("");  // Clears Q&A input
                  setAnswer(null);  // Clears previous answer
                  setQaAudioUrl(""); // Clears Q&A audio
                }}
              >
                Choose Another File
              </button>
            )}
          </div>

          {image && (
            <div className="image-section">
              <img src={image} alt="Uploaded Preview" />
            </div>
          )}

          <div className="caption-section">
            {loadingCaption ? (
              <p className="loading">Generating Caption...</p>
            ) : (
              caption && (
                <>
                  <p className="caption">Caption: {caption}</p>
                  {captionAudioUrl && (
                    <div className="audio-controls">
                      <h3>🔊 Caption Audio</h3>
                      <audio controls>
                        <source src={captionAudioUrl} type="audio/mpeg" />
                        Your browser does not support the audio element.
                      </audio>
                    </div>
                  )}
                </>
              )
            )}
          </div>
        </div>

        {/* Q&A Section (Right) */}
        <div className="qa-container">
          <h2>Ask a Question About the Image</h2>
          <div className="qa-section">
            <input
              type="text"
              placeholder="Ask a question..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAskQuestion()}
            />
            <button onClick={handleAskQuestion}>Get Answer</button>
          </div>

          {answer !== null && (
            <div className="answer-section">
              {loadingAnswer ? (
                <p className="loading">Processing answer...</p>
              ) : (
                answer && (
                  <>
                    <p className="answer">Answer: {answer}</p>
                    {qaAudioUrl && (
                      <div className="audio-controls">
                        <h3>🔊 Answer Audio</h3>
                        <audio controls>
                          <source src={qaAudioUrl} type="audio/mpeg" />
                          Your browser does not support the audio element.
                        </audio>
                      </div>
                    )}
                  </>
                )
              )}
            </div>


          )}
        </div>
      </div>
    </div>
  );
}

export default App;
