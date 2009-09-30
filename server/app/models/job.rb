class Job < ActiveRecord::Base
  has_many :tasks

  def status_string
    @status = self[:status]
    if @status == 0:
      return 'waiting'
    elsif @status == 1:
      return 'queued'
    elsif @status == 2:
      return 'running'
    elsif @status == 3:
      return 'finished'
    elsif @status == -3:
      return 'error'
    elsif @status == -2:
      return 'stopped'
    elsif @status == -1:
      return 'paused'
    end
    return self[:status]
  end

end
