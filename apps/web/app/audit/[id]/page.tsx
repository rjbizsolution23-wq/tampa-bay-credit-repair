import { ConsultationForm } from "@/components/audit/ConsultationForm"
import { notFound } from "next/navigation"

// This would typically fetch from the API
async function getAuditData(id: string) {
    // In a real SSR scenario, you'd call your internal service or API URL
    // const res = await fetch(`http://localhost:8000/api/blueprint/${id}`, { cache: 'no-store' })
    // if (!res.ok) return undefined
    // return res.json()

    // For demonstration, returning mock data if API isn't running
    return {
        id: id,
        scores: { transunion: 620, equifax: 615, experian: 630 },
        summary: {
            totalViolationsFound: 3,
            utilizationPercentage: 45,
            totalCollections: 2,
            needsStarterAccounts: false
        },
        itemsForReview: [
            {
                id: "item-1",
                creditorName: "CAPITAL ONE",
                accountNumber: "XXXX-1234",
                bureau: "TransUnion",
                suggestedResolution: "GENERAL_DISPUTE",
                violationCount: 0,
                priorityLevel: 3,
                resolutionOptions: [
                    { value: 'GENERAL_DISPUTE', label: 'General Dispute', description: 'Standard dispute' },
                    { value: 'FCRA_VIOLATION', label: 'FCRA Violation', description: 'Specific violation' }
                ]
            },
            {
                id: "item-2",
                creditorName: "MIDLAND FUNDING",
                accountNumber: "XXXX-9876",
                bureau: "Equifax",
                suggestedResolution: "DEBT_VALIDATION",
                violationCount: 2,
                priorityLevel: 5,
                resolutionOptions: [
                    { value: 'DEBT_VALIDATION', label: 'Debt Validation', description: 'Request proof of debt' },
                    { value: 'PAY_FOR_DELETE', label: 'Pay for Delete', description: 'Negotiate removal' }
                ]
            }
        ]
    }
}

export default async function AuditPage({ params }: { params: { id: string } }) {
    const auditData = await getAuditData(params.id)

    if (!auditData) {
        notFound()
    }

    return (
        <main className="min-h-screen bg-background">
            <div className="py-6">
                <ConsultationForm auditData={auditData} />
            </div>
        </main>
    )
}
