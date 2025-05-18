import useSWR from 'swr';

const fetcher = (url: string) => fetch(url).then(res => res.json());

export default function AgentDashboard() {
    const {data: agents, error} = useSWR('/api/agents', fetcher, {refreshInterval: 5000}); // Poll every 5s for live
    console.log(agents);
    console.log("error", error);
    if (error) return <div>Error loading agents.</div>;
    if (!agents) return <div>Loading agents...</div>;

    return (
        <div className="p-4">
            <h2 className="text-xl font-bold mb-2">Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {agents.map((agent: any) => (
                    <div key={agent.name} className="bg-white shadow rounded p-4 flex flex-col items-start">
                        <div className="flex items-center mb-2">
                            <span className="font-semibold">{agent.name}</span>
                            <span className="ml-2 text-sm text-gray-500">({agent.role})</span>
                        </div>
                        <div>
                            <span>Zone: {agent.zone || "Unknown"}</span>
                        </div>
                        <div className="mt-2 flex items-center">
              <span className={`emotion-badge emotion-${(agent.emotion || 'neutral').toLowerCase()}`}>
                {agent.emotion || "Neutral"}
              </span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}