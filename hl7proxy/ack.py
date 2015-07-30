'''
Creates HL7 ACK responses for the HL7 proxy
'''

import hl7
from datetime import datetime

def ACK(original_message, ack_code='AR'):
    """
    Build a basic ACK message

    ``ack_code`` options are one of `AA` (accept), `AR` (reject), `AE` (error) (2.15.8)
    """
    # hl7.parse requires the message is unicode already or can be easily converted via unicode()
    msg = hl7.parse(original_message)
    ack_response = create_msh_response(msg, ack_code)
    return unicode(ack_response)

def create_msh_response(msg, response_type='AA'):
    ''' create the msh msa response '''
    SEP = '|^~\&'
    CR_SEP = '\r'

    msh = msg.segment('MSH')
    control_id = unicode(msg.segment('MSH')[9])

    msh_response = hl7.Segment(SEP[0], [
                        hl7.Field(SEP[1], ['MSH']),
                        hl7.Field('', SEP[1:]),
                        hl7.Field('', msh[4]),
                        hl7.Field('', msh[5]),
                        hl7.Field('', msh[2]),
                        hl7.Field('', msh[3]),
                        hl7.Field('', datetime.now().strftime('%Y%m%d%H%M%S')),
                        hl7.Field('', 'ACK'),
                        hl7.Field('', control_id),
                        hl7.Field('', msh[10]),
                        hl7.Field('', msh[11])
                     ])
    msa_response = hl7.Segment(SEP[0], [
                        hl7.Field(SEP[1], ['MSA']),
                        hl7.Field('', response_type),
                        hl7.Field('', control_id)
                     ])
    response = hl7.Message(CR_SEP, [msh_response, msa_response])
    return response