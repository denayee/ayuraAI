const PREDICTION_BASE_URL = window.BASE_URL || "https://ayuraai.onrender.com";

async function submitPrediction(userData) {
  try {
    const { response, result } = await window.AyuraApi.jsonRequest(`${PREDICTION_BASE_URL}/predict`, {
      method: "POST",
      data: userData,
    });

    if (!response.ok || !result.success) {
      throw new Error(result.error || "Prediction request failed.");
    }

    console.log(result);
    return result;
  } catch (error) {
    console.error("Prediction request failed:", error);
    throw error;
  }
}
