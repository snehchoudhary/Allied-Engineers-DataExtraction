export const processData = async (file, analyses, thresholds) => {
  const formData = new FormData();
  formData.append("file", file);
  analyses.forEach((analysis) => formData.append("selections", analysis));
  formData.append("acpsp_threshold", thresholds.ACPSP || 4);
  formData.append("attenuation_threshold", thresholds.Attenuation || 2);
  formData.append("cpcips_threshold", thresholds.CPCIPS || -1);

  const res = await fetch("http://localhost:8000/process-data/", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) throw new Error("Failed to process data");

  return await res.blob();
};
