import {FormEvent, useEffect, useMemo, useState} from "react";
import QRCode from "qrcode";

import {
    getTwoFactorStatus,
    startTwoFactorEnrollment,
    verifyTwoFactor,
    disableTwoFactor,
    TwoFactorStatus,
    TwoFactorSetup,
} from "../api";
import {useNotification} from "../contexts/NotificationContext";
import {useErrorHandler} from "../utils/errorHandling";

interface EnrollmentState extends TwoFactorSetup {
    qrDataUrl?: string;
}

const formatTimestamp = (value?: string | null) => {
    if (!value) return "—";
    try {
        return new Date(value).toLocaleString();
    } catch {
        return value;
    }
};

const normalizeCode = (value: string) => value.replace(/[^0-9]/g, "").slice(0, 8);

export default function SecurityPanel() {
    const [status, setStatus] = useState<TwoFactorStatus | null>(null);
    const [enrollment, setEnrollment] = useState<EnrollmentState | null>(null);
    const [verifyCode, setVerifyCode] = useState("");
    const [disableCode, setDisableCode] = useState("");
    const [isBusy, setIsBusy] = useState<Record<string, boolean>>({});

    const {addNotification} = useNotification();
    const {handleApiError} = useErrorHandler();

    const refreshStatus = async () => {
        try {
            const data = await getTwoFactorStatus();
            if (!data) {
                throw new Error("No status data returned");
            }
            setStatus(data);
        } catch (error) {
            handleApiError(error, "Failed to fetch two-factor status");
        }
    };

    useEffect(() => {
        void refreshStatus();
    }, []);

    useEffect(() => {
        if (status && !status.pending) {
            setEnrollment(null);
            setVerifyCode("");
        }
    }, [status?.pending]);

    const beginEnrollment = async () => {
        setIsBusy(prev => ({...prev, setup: true}));
        try {
            const result = await startTwoFactorEnrollment();
            if (!result) {
                throw new Error("Failed to start enrollment");
            }
            const qrDataUrl = await QRCode.toDataURL(result.otpauth_url);
            setEnrollment({...result, qrDataUrl});
            addNotification({
                type: "success",
                message: "Two-factor enrollment initiated. Scan the QR code and verify a code to finish.",
                duration: 5000,
            });
            await refreshStatus();
        } catch (error) {
            handleApiError(error, "Failed to start two-factor enrollment");
        } finally {
            setIsBusy(prev => ({...prev, setup: false}));
        }
    };

    const submitVerification = async (event: FormEvent) => {
        event.preventDefault();
        if (!verifyCode) return;
        setIsBusy(prev => ({...prev, verify: true}));
        try {
            const response = await verifyTwoFactor(verifyCode);
            if (!response) {
                throw new Error("Verification API returned no data");
            }
            addNotification({
                type: "success",
                message: "Two-factor authentication enabled.",
                duration: 4000,
            });
            setVerifyCode("");
            setEnrollment(null);
            await refreshStatus();
        } catch (error) {
            handleApiError(error, "Invalid verification code");
        } finally {
            setIsBusy(prev => ({...prev, verify: false}));
        }
    };

    const submitDisable = async (event: FormEvent) => {
        event.preventDefault();
        if (!disableCode && status?.enabled) return;
        setIsBusy(prev => ({...prev, disable: true}));
        try {
            const response = await disableTwoFactor(disableCode);
            if (!response) {
                throw new Error("Disable API returned no data");
            }
            addNotification({
                type: "success",
                message: "Two-factor authentication disabled.",
                duration: 4000,
            });
            setDisableCode("");
            await refreshStatus();
        } catch (error) {
            handleApiError(error, "Failed to disable two-factor authentication");
        } finally {
            setIsBusy(prev => ({...prev, disable: false}));
        }
    };

    const active = status?.status === "active";
    const pending = status?.pending;

    const enrollmentContent = useMemo(() => {
        if (!enrollment) return null;
        return (
            <div className="mt-4 space-y-3" data-testid="two-factor-enrollment">
                <div className="p-3 rounded bg-slate-50 border border-slate-200">
                    <h4 className="font-semibold text-sm text-slate-700">Scan in your authenticator</h4>
                    {enrollment.qrDataUrl ? (
                        <img
                            src={enrollment.qrDataUrl}
                            alt="TOTP QR code"
                            className="mx-auto mt-2 w-40 h-40"
                        />
                    ) : (
                        <div className="text-xs text-slate-500">Preparing QR code…</div>
                    )}
                    <p className="text-xs text-slate-600 mt-3 break-all">
                        Secret: <span className="font-mono">{enrollment.secret}</span>
                    </p>
                </div>

                <form onSubmit={submitVerification} className="space-y-2">
                    <label className="block text-sm font-medium text-slate-700" htmlFor="verify-code">
                        Enter a 6-digit code to finalize setup
                    </label>
                    <input
                        id="verify-code"
                        type="text"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        value={verifyCode}
                        onChange={(event) => setVerifyCode(normalizeCode(event.target.value))}
                        className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="123 456"
                        maxLength={8}
                        required
                    />
                    <button
                        type="submit"
                        className="w-full md:w-auto px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
                        disabled={isBusy.verify}
                        data-testid="two-factor-verify"
                    >
                        {isBusy.verify ? "Verifying…" : "Verify & Enable"}
                    </button>
                </form>
            </div>
        );
    }, [enrollment, verifyCode, isBusy.verify]);

    return (
        <section className="p-4 border rounded-xl shadow bg-white" aria-labelledby="security-panel-heading">
            <div className="flex items-center justify-between">
                <h2 id="security-panel-heading" className="font-semibold text-slate-800">Security</h2>
                <button
                    onClick={() => void refreshStatus()}
                    className="text-sm text-blue-600 hover:underline"
                >
                    Refresh
                </button>
            </div>

            <dl className="mt-3 grid grid-cols-1 gap-2 text-sm text-slate-600">
                <div className="flex justify-between">
                    <dt>Status</dt>
                    <dd className={`font-medium ${active ? "text-green-600" : pending ? "text-amber-600" : "text-slate-700"}`}>
                        {status ? status.status.toUpperCase() : "loading…"}
                    </dd>
                </div>
                <div className="flex justify-between">
                    <dt>Version</dt>
                    <dd>{status?.version ?? "—"}</dd>
                </div>
                <div className="flex justify-between">
                    <dt>Last verified</dt>
                    <dd>{formatTimestamp(status?.last_verified_at)}</dd>
                </div>
            </dl>

            <div className="mt-4 space-y-4">
                {active ? (
                    <form onSubmit={submitDisable} className="space-y-2" data-testid="two-factor-disable">
                        <label className="block text-sm font-medium text-slate-700" htmlFor="disable-code">
                            Enter a recent code to disable
                        </label>
                        <input
                            id="disable-code"
                            type="text"
                            inputMode="numeric"
                            pattern="[0-9]*"
                            value={disableCode}
                            onChange={(event) => setDisableCode(normalizeCode(event.target.value))}
                            className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                            placeholder="123 456"
                            maxLength={8}
                            required
                        />
                        <button
                            type="submit"
                            className="w-full md:w-auto px-3 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 disabled:opacity-50"
                            disabled={isBusy.disable}
                        >
                            {isBusy.disable ? "Disabling…" : "Disable Two-Factor"}
                        </button>
                    </form>
                ) : (
                    <div className="space-y-2">
                        <p className="text-sm text-slate-600">
                            Protect sensitive controls by enabling TOTP-based two-factor authentication.
                        </p>
                        <button
                            type="button"
                            onClick={() => void beginEnrollment()}
                            className="w-full md:w-auto px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-50"
                            disabled={isBusy.setup}
                            data-testid="two-factor-setup"
                        >
                            {pending ? "Reissue Enrollment" : "Enable Two-Factor"}
                        </button>
                    </div>
                )}

                {pending && !enrollment && (
                    <div className="p-3 bg-amber-50 border border-amber-200 rounded text-sm text-amber-700">
                        Enrollment pending confirmation. Provide a current authenticator code to finish setup.
                    </div>
                )}

                {enrollmentContent}
            </div>
        </section>
    );
}
