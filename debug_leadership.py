from src.backend.app.services.leadership.simulation_service import LeadershipSimulationService

service = LeadershipSimulationService()
try:
    sim = service.create_simulation('test_user', difficulty='medium')
    print('simulation created', sim.simulation_id)
    print('project:', sim.project.name)
    print('team size', len(sim.team))
    print('scenarios', len(sim.scenarios))
except Exception as e:
    import traceback
    traceback.print_exc()
