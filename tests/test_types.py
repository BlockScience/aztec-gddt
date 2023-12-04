from aztec_gddt.types import Process, SelectionPhase

def test_process_instance():
    p = Process(uuid=1, 
                current_phase_init_time=0, 
                duration_in_current_phase=0,
                phase = SelectionPhase.pending_proposals)