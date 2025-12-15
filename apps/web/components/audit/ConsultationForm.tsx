"use client"

import * as React from "react"
import { useForm } from "react-hook-form" // Assuming react-hook-form is available or will be processed
import { Button } from "@/components/ui/button"
import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { toast } from "sonner"

// Mock data integration interface
interface AuditData {
    id: string
    scores: { transunion: number; equifax: number; experian: number }
    summary: any
    itemsForReview: any[]
}

export function ConsultationForm({
    auditData
}: {
    auditData: AuditData
}) {
    const [currentStep, setCurrentStep] = React.useState(0)
    const [formData, setFormData] = React.useState<any>({})
    const [itemResolutions, setItemResolutions] = React.useState<Record<string, string>>({})

    const steps = [
        "Review Scores",
        "Client Info",
        "Financial Goals",
        "Audit Items",
        "Finalize"
    ]

    const handleNext = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1)
        }
    }

    const handleBack = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1)
        }
    }

    const handleComplete = async () => {
        try {
            const response = await fetch(`/api/blueprint/${auditData.id}/complete`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    consultation: formData,
                    resolutions: itemResolutions
                })
            })

            if (response.ok) {
                toast.success("Consultation completed!", {
                    description: "Blueprint is generating in the background."
                })
            } else {
                toast.error("Failed to complete consultation")
            }
        } catch (error) {
            toast.error("Error submitting form")
        }
    }

    return (
        <div className="container mx-auto py-10 max-w-4xl">
            <div className="mb-8">
                <h2 className="text-3xl font-bold tracking-tight">Audit Consultation</h2>
                <p className="text-muted-foreground">
                    Step {currentStep + 1} of {steps.length}: {steps[currentStep]}
                </p>
                <div className="mt-4 h-2 w-full bg-secondary rounded-full">
                    <div
                        className="h-full bg-primary rounded-full transition-all duration-300"
                        style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                    />
                </div>
            </div>

            {currentStep === 0 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Credit Score Overview</CardTitle>
                        <CardDescription>Initial scores at time of audit</CardDescription>
                    </CardHeader>
                    <CardContent className="grid gap-6 md:grid-cols-3">
                        {Object.entries(auditData.scores).map(([bureau, score]) => (
                            <Card key={bureau} className="text-center py-6">
                                <CardTitle className="text-4xl text-primary">{score || 'N/A'}</CardTitle>
                                <p className="text-sm font-medium uppercase mt-2 text-muted-foreground">{bureau}</p>
                                <Badge variant={score && score > 700 ? "default" : "secondary"} className="mt-2">
                                    {score && score > 700 ? "Good" : "Needs Work"}
                                </Badge>
                            </Card>
                        ))}
                    </CardContent>
                    <CardFooter>
                        <Button onClick={handleNext} className="w-full">Next: Client Information</Button>
                    </CardFooter>
                </Card>
            )}

            {currentStep === 1 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Client Information</CardTitle>
                        <CardDescription>Verify basic client details</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="firstName">First Name</Label>
                                <Input
                                    id="firstName"
                                    value={formData.firstName || ""}
                                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="lastName">Last Name</Label>
                                <Input
                                    id="lastName"
                                    value={formData.lastName || ""}
                                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                value={formData.email || ""}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="phone">Phone</Label>
                            <Input
                                id="phone"
                                value={formData.phone || ""}
                                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                            />
                        </div>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="outline" onClick={handleBack}>Back</Button>
                        <Button onClick={handleNext}>Next: Financial Goals</Button>
                    </CardFooter>
                </Card>
            )}

            {currentStep === 2 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Financial Profile & Goals</CardTitle>
                        <CardDescription>Understanding client objectives</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>Primary Goal</Label>
                            <Select onValueChange={(val) => setFormData({ ...formData, primaryGoal: val })}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select a goal" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="buy_home">Buy a Home</SelectItem>
                                    <SelectItem value="buy_car">Buy a Car</SelectItem>
                                    <SelectItem value="lower_rates">Lower Interest Rates</SelectItem>
                                    <SelectItem value="general">General Improvement</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="space-y-2">
                                <Label>Monthly Income</Label>
                                <Input
                                    type="number"
                                    placeholder="0.00"
                                    onChange={(e) => setFormData({ ...formData, monthlyIncome: e.target.value })}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Rent vs Own</Label>
                                <Select onValueChange={(val) => setFormData({ ...formData, rentOrOwn: val })}>
                                    <SelectTrigger>
                                        <SelectValue placeholder="Select one" />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="rent">Rent</SelectItem>
                                        <SelectItem value="own">Own</SelectItem>
                                        <SelectItem value="family">Live with Family</SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="outline" onClick={handleBack}>Back</Button>
                        <Button onClick={handleNext}>Next: Audit Items</Button>
                    </CardFooter>
                </Card>
            )}

            {currentStep === 3 && (
                <Card>
                    <CardHeader>
                        <CardTitle>BluePint Audit Items Review</CardTitle>
                        <CardDescription>Review and set resolution strategies for {auditData.itemsForReview?.length || 0} items</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {auditData.itemsForReview?.map((item) => (
                            <div key={item.id} className="border rounded-lg p-4 space-y-3">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h4 className="font-semibold text-lg">{item.creditorName}</h4>
                                        <p className="text-sm text-muted-foreground">{item.accountNumber} • {item.bureau}</p>
                                    </div>
                                    <Badge variant={item.priorityLevel > 3 ? "destructive" : "default"}>
                                        Priority: {item.priorityLevel}
                                    </Badge>
                                </div>

                                {item.violationCount > 0 && (
                                    <div className="bg-red-50 dark:bg-red-950/20 p-2 rounded text-sm text-red-600 dark:text-red-400">
                                        ⚠️ {item.violationCount} FCRA Violation(s) Detected
                                    </div>
                                )}

                                <div className="space-y-2">
                                    <Label>Resolution Strategy</Label>
                                    <Select
                                        defaultValue={item.suggestedResolution}
                                        onValueChange={(val) => setItemResolutions({ ...itemResolutions, [item.id]: val })}
                                    >
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            {item.resolutionOptions?.map((opt: any) => (
                                                <SelectItem key={opt.value} value={opt.value}>
                                                    {opt.label}
                                                </SelectItem>
                                            ))}
                                        </SelectContent>
                                    </Select>
                                    <p className="text-xs text-muted-foreground">
                                        {item.resolutionOptions?.find((o: any) => o.value === (itemResolutions[item.id] || item.suggestedResolution))?.description}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="outline" onClick={handleBack}>Back</Button>
                        <Button onClick={handleNext}>Next: Finalize</Button>
                    </CardFooter>
                </Card>
            )}

            {currentStep === 4 && (
                <Card>
                    <CardHeader>
                        <CardTitle>Ready to Complete</CardTitle>
                        <CardDescription>Review notes and generate blueprint</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <Label>Consultant Notes</Label>
                            <Textarea
                                placeholder="Any specific notes for this client..."
                                onChange={(e) => setFormData({ ...formData, consultantNotes: e.target.value })}
                            />
                        </div>
                        <div className="flex items-center space-x-2">
                            <Switch
                                id="email-client"
                                onCheckedChange={(c) => setFormData({ ...formData, emailClient: c })}
                            />
                            <Label htmlFor="email-client">Email Blueprint to Client immediately</Label>
                        </div>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="outline" onClick={handleBack}>Back</Button>
                        <Button onClick={handleComplete} size="lg" className="w-full ml-4">Complete & Generate Blueprint PDF</Button>
                    </CardFooter>
                </Card>
            )}
        </div>
    )
}
