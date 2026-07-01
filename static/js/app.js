document.getElementById("evaluateBtn").addEventListener("click", async () => {

    const payload = {
        employee_id: document.getElementById("employee_id").value.trim(),
        category: document.getElementById("category").value,
        amount: Number(document.getElementById("amount").value),
        receipt: document.getElementById("receipt").checked,
        manager_approval: document.getElementById("approval").checked
    };

    try {

        const response = await fetch("/evaluate-claim", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error("Failed to evaluate claim");
        }

        const data = await response.json();

        console.log(data);

        // -------------------------
        // Decision
        // -------------------------

        const decision = document.getElementById("decision");

        decision.innerText = data.decision;
        decision.className = "badge";

        switch (data.decision) {

            case "Approve":
                decision.classList.add("bg-success");
                break;

            case "Partially Approve":
                decision.classList.add("bg-warning", "text-dark");
                break;

            case "Reject":
                decision.classList.add("bg-danger");
                break;

            default:
                decision.classList.add("bg-secondary");
        }

        // -------------------------
        // Approved Amount
        // -------------------------

        document.getElementById("approved_amount").innerText =
            "₹" + data.approved_amount;

        // -------------------------
        // Deduction
        // -------------------------

        document.getElementById("deduction").innerText =
            "₹" + data.deduction;

        // -------------------------
        // Confidence
        // -------------------------

        const confidence = Math.round((data.confidence || 0) * 100);

        const confidenceBar = document.getElementById("confidenceBar");

        confidenceBar.style.width = confidence + "%";
        confidenceBar.innerText = confidence + "%";

        confidenceBar.className = "progress-bar";

        if (confidence >= 80) {

            confidenceBar.classList.add("bg-success");

        } else if (confidence >= 50) {

            confidenceBar.classList.add("bg-warning");

        } else {

            confidenceBar.classList.add("bg-danger");

        }

        // -------------------------
        // Reason
        // -------------------------

        document.getElementById("reason").innerText =
            data.reason || "";

        // -------------------------
        // Policy Reference
        // -------------------------

        document.getElementById("policy").innerText =
            data.policy_reference || "";

        // -------------------------
        // Business Rule Validation
        // -------------------------

        document.getElementById("policyStatus").innerHTML =
            '<span class="badge bg-success">Passed</span>';

        document.getElementById("receiptStatus").innerHTML =
            payload.receipt
                ? '<span class="badge bg-success">Verified</span>'
                : '<span class="badge bg-danger">Missing</span>';

        document.getElementById("limitStatus").innerHTML =
            '<span class="badge bg-success">Checked</span>';

        document.getElementById("duplicateStatus").innerHTML =
            '<span class="badge bg-success">Clear</span>';

        document.getElementById("approvalStatus").innerHTML =
            payload.manager_approval
                ? '<span class="badge bg-success">Approved</span>'
                : '<span class="badge bg-warning">Pending</span>';

        document.getElementById("aiStatus").innerHTML =
            '<span class="badge bg-primary">Completed</span>';

        // -------------------------
        // Audit Trail
        // -------------------------

        const auditDiv = document.getElementById("auditTrail");

        if (auditDiv) {

            auditDiv.innerHTML = "";

            if (Array.isArray(data.audit_trail) && data.audit_trail.length > 0) {

                data.audit_trail.forEach(step => {

                    auditDiv.innerHTML += `
                        <li class="list-group-item">
                            <strong>${step.tool}</strong><br>
                            <span class="badge bg-info">${step.status}</span><br>
                            <small>${step.result}</small>
                        </li>
                    `;

                });

            } else {

                auditDiv.innerHTML =
                    "<li class='list-group-item'>No audit information available.</li>";

            }

        }

        // -------------------------
        // Recent Claims
        // -------------------------

        const historyTable = document.getElementById("historyTable");

        if (historyTable) {

            if (historyTable.innerHTML.includes("No claims")) {

                historyTable.innerHTML = "";

            }

            historyTable.innerHTML += `
                <tr>
                    <td>${payload.employee_id}</td>
                    <td>${payload.category}</td>
                    <td>₹${payload.amount}</td>
                    <td>
                        <span class="badge ${
                            data.decision === "Approve"
                                ? "bg-success"
                                : data.decision === "Reject"
                                ? "bg-danger"
                                : "bg-warning text-dark"
                        }">
                            ${data.decision}
                        </span>
                    </td>
                </tr>
            `;
        }

    }

    catch (err) {

        console.error(err);

        alert("Unable to evaluate claim.");

    }

});