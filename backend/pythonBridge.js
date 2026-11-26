const { spawn } = require("child_process");
const path = require("path");

/**
 * Call the Python prediction script with the given payload.
 * Resolves with the parsed JSON result, or rejects with an error.
 */
function predictWithPython(payload) {
  return new Promise((resolve, reject) => {
    // Resolve python executable: prefer venv python on Windows, fallback to "python"
    const projectRoot = path.resolve(__dirname, "..");
    const venvPython = path.join(projectRoot, ".venv", "Scripts", "python.exe");
    const pythonExecutable = require("fs").existsSync(venvPython)
      ? venvPython
      : "python";

    const scriptPath = path.join(projectRoot, "ml", "predict.py");

    const child = spawn(pythonExecutable, [scriptPath], {
      cwd: projectRoot,
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    child.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    child.on("error", (err) => {
      reject(new Error(`Failed to start Python process: ${err.message}`));
    });

    child.on("close", (code) => {
      if (code !== 0) {
        return reject(
          new Error(
            `Python script exited with code ${code}. stderr: ${stderr}`
          )
        );
      }
      try {
        const result = JSON.parse(stdout);
        if (result.error) {
          return reject(new Error(result.error));
        }
        resolve(result);
      } catch (e) {
        reject(
          new Error(
            `Failed to parse Python output: ${e.message}. Raw output: ${stdout}`
          )
        );
      }
    });

    // Send payload to Python via stdin
    child.stdin.write(JSON.stringify(payload));
    child.stdin.end();
  });
}

module.exports = { predictWithPython };